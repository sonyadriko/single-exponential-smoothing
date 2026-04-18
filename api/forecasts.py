from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Union
from datetime import datetime, date
import pandas as pd

import models
from database import get_db
from schemas.forecasts import (
    ForecastRequest,
    ForecastResponse,
    ForecastOut,
    ForecastCreateResponse,
    ForecastProjectInfo,
    ForecastProjectDetail
)
from repositories.forecast_repository import ForecastRepository
from repositories.sale_repository import SaleRepository
from api.auth import get_current_user_or_session, get_admin_user_or_session
from services.forecast_service import (
    calculate_ses_with_steps,
    calculate_next_period_forecast
)

router = APIRouter()


def parse_date(value: Union[str, date]) -> date:
    """Convert string to date object if needed."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ValueError(f"Invalid date: {value}")


def date_to_iso(d: Union[date, str, None]) -> Union[str, None]:
    """Convert date to ISO string for JSON serialization."""
    if d is None:
        return None
    if isinstance(d, date):
        return d.isoformat()
    return d


@router.post("")
async def create_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user_or_session)
):
    """Create a forecast using Single Exponential Smoothing (admin only)."""
    sale_repo = SaleRepository(db)
    forecast_repo = ForecastRepository(db)

    # Get sales data
    sales_query = sale_repo.get_all_ordered()

    # Filter by product
    if request.product_name:
        sales_query = [s for s in sales_query if s.product_name == request.product_name]

    # Filter by date range (convert strings to date objects for comparison)
    start_date = parse_date(request.start_date) if request.start_date else None
    end_date = parse_date(request.end_date) if request.end_date else None
    next_period_date = parse_date(request.next_period_date) if request.next_period_date else None

    if start_date:
        sales_query = [s for s in sales_query if s.date >= start_date]
    if end_date:
        sales_query = [s for s in sales_query if s.date <= end_date]

    if not sales_query:
        raise HTTPException(status_code=400, detail="No data available for the specified filters")

    # Convert date objects to ISO strings for JSON serialization
    data = [{"date": date_to_iso(s.date), "product_name": s.product_name, "qty": s.qty} for s in sales_query]
    df = pd.DataFrame(data)
    # Ensure dates remain as strings (pandas might convert to datetime)
    df["date"] = df["date"].astype(str)

    results: Dict[str, Any] = {}
    total_mape = 0
    product_count = 0

    for product_name, group in df.groupby("product_name"):
        group = group.sort_values("date")
        dates = group["date"].tolist()  # Ensure strings
        actuals = group["qty"].tolist()

        # Calculate SES
        calc_result = calculate_ses_with_steps(actuals, dates, request.alpha)
        forecasts = calc_result["forecasts"]
        steps = calc_result["steps"]
        mape = calc_result["mape"]

        # Calculate next period forecast
        next_forecast = calculate_next_period_forecast(actuals[-1], forecasts[-1], request.alpha)

        # Save forecast to database (convert dates to ISO strings for JSON)
        forecast_repo.create_forecast(
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            created_by=current_user.id,
            alpha=request.alpha,
            product_name=product_name,
            next_period_forecast=next_forecast,
            next_period_date=next_period_date,
            mape=mape,
            calculation_steps={
                "dates": [date_to_iso(d) for d in dates],
                "actuals": actuals,
                "forecasts": forecasts,
                "steps": steps
            }
        )

        results[product_name] = {
            "dates": dates,
            "actuals": actuals,
            "forecasts": forecasts,
            "steps": steps,
            "mape": mape,
            "next_period_forecast": next_forecast,
            "next_period_date": date_to_iso(next_period_date)
        }
        total_mape += mape
        product_count += 1

    return {
        "results": results,
        "overall_mape": total_mape / product_count if product_count > 0 else 0,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/latest")
async def get_latest_forecast(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_session)
):
    """Get the most recent forecast."""
    forecast_repo = ForecastRepository(db)
    latest = forecast_repo.get_latest()

    if not latest:
        raise HTTPException(status_code=404, detail="No forecast found")

    steps = latest.calculation_steps or {}
    return {
        "id": latest.id,
        "created_at": latest.created_at.isoformat(),
        "alpha": latest.alpha,
        "product_name": latest.product_name,
        "next_period_forecast": latest.next_period_forecast,
        "next_period_date": latest.next_period_date,
        "mape": latest.mape,
        "dates": steps.get("dates", []),
        "actuals": steps.get("actuals", []),
        "forecasts": steps.get("forecasts", []),
        "steps": steps.get("steps", [])
    }


@router.get("/history", response_model=list[ForecastOut])
async def get_forecast_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_session)
):
    """Get all forecasts history."""
    forecast_repo = ForecastRepository(db)
    forecasts = forecast_repo.get_all_ordered()
    return [{
        "id": f.id,
        "created_at": f.created_at.isoformat(),
        "alpha": f.alpha,
        "product_name": f.product_name,
        "next_period_forecast": f.next_period_forecast,
        "next_period_date": f.next_period_date,
        "mape": f.mape
    } for f in forecasts]


@router.get("/projects", response_model=list[ForecastProjectInfo])
async def get_forecast_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user_or_session)
):
    """Get all forecast projects (admin only)."""
    forecast_repo = ForecastRepository(db)
    return forecast_repo.get_project_summaries()


@router.get("/project/{project_name}")
async def get_forecast_project(
    project_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_session)
):
    """Get details of a specific forecast project."""
    forecast_repo = ForecastRepository(db)
    forecasts = forecast_repo.get_by_project(project_name)

    if not forecasts:
        raise HTTPException(status_code=404, detail="Project not found")

    results = {}
    for f in forecasts:
        steps = f.calculation_steps or {}
        results[f.product_name] = {
            "dates": steps.get("dates", []),
            "actuals": steps.get("actuals", []),
            "forecasts": steps.get("forecasts", []),
            "steps": steps.get("steps", []),
            "mape": f.mape,
            "next_period_forecast": f.next_period_forecast,
            "next_period_date": f.next_period_date
        }

    overall_mape = sum(f.mape for f in forecasts) / len(forecasts) if forecasts else 0

    return {
        "project_name": project_name,
        "created_at": forecasts[0].created_at.isoformat(),
        "alpha": forecasts[0].alpha,
        "results": results,
        "overall_mape": overall_mape
    }


@router.put("/project/{project_name}")
async def update_forecast_project(
    project_name: str,
    new_name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user_or_session)
):
    """Rename a forecast project (admin only)."""
    forecast_repo = ForecastRepository(db)
    if not forecast_repo.update_project_name(project_name, new_name):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "ok", "msg": "Project renamed"}


@router.delete("/project/{project_name}")
async def delete_forecast_project(
    project_name: str,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user_or_session)
):
    """Delete a forecast project (admin only)."""
    forecast_repo = ForecastRepository(db)
    count = forecast_repo.delete_project(project_name)
    if count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "ok", "msg": f"Deleted {count} forecast(s)"}


@router.post("/reset-data")
async def reset_data(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user_or_session)
):
    """Reset sales and forecasts data, then reseed May data (admin only)."""
    from services.seed_service import SeedService

    # Clear data
    db.query(models.Sale).delete()
    db.query(models.Forecast).delete()

    # Reseed
    seed_service = SeedService(db)
    seed_service.seed_may_data()

    return {"status": "ok", "msg": "Data reset to initial May state"}
