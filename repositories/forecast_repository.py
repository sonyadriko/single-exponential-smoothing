from typing import List, Optional, Union
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from repositories.base import BaseRepository


class ForecastRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(models.Forecast, db)

    def get_latest(self) -> Optional[models.Forecast]:
        return self.db.query(models.Forecast).order_by(models.Forecast.created_at.desc()).first()

    def get_all_ordered(self) -> List[models.Forecast]:
        return self.db.query(models.Forecast).order_by(models.Forecast.created_at.desc()).all()

    def get_by_project(self, project_name: str) -> List[models.Forecast]:
        return self.db.query(models.Forecast).filter(
            models.Forecast.project_name == project_name
        ).all()

    def create_forecast(
        self,
        project_name: Optional[str],
        created_at,
        created_by: int,
        alpha: float,
        product_name: str,
        next_period_forecast: float,
        next_period_date: Optional[Union[str, date]],
        mape: float,
        calculation_steps: dict
    ) -> models.Forecast:
        forecast = models.Forecast(
            project_name=project_name,
            created_at=created_at,
            created_by=created_by,
            alpha=alpha,
            product_name=product_name,
            next_period_forecast=next_period_forecast,
            next_period_date=next_period_date,
            mape=mape,
            calculation_steps=calculation_steps
        )
        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)
        return forecast

    def get_project_summaries(self) -> List[dict]:
        """Get summary of all forecast projects."""
        projects = self.db.query(
            models.Forecast.project_name,
            func.min(models.Forecast.created_at).label('created_at'),
            func.min(models.User.username).label('created_by'),
            func.min(models.Forecast.alpha).label('alpha'),
            func.count(models.Forecast.id).label('forecast_count'),
            func.avg(models.Forecast.mape).label('overall_mape')
        ).join(
            models.User, models.User.id == models.Forecast.created_by
        ).filter(
            models.Forecast.project_name.isnot(None)
        ).group_by(
            models.Forecast.project_name
        ).all()

        return [{
            "project_name": p.project_name,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "created_by": p.created_by,
            "alpha": p.alpha,
            "forecast_count": p.forecast_count,
            "overall_mape": p.overall_mape
        } for p in projects]

    def update_project_name(self, project_name: str, new_name: str) -> bool:
        forecasts = self.get_by_project(project_name)
        if not forecasts:
            return False
        for f in forecasts:
            f.project_name = new_name
        self.db.commit()
        return True

    def delete_project(self, project_name: str) -> int:
        forecasts = self.get_by_project(project_name)
        if not forecasts:
            return 0
        count = len(forecasts)
        for f in forecasts:
            self.db.delete(f)
        self.db.commit()
        return count

    def delete_all(self) -> int:
        count = self.db.query(models.Forecast).delete()
        self.db.commit()
        return count
