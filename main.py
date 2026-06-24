from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from api import auth, sales, products, forecasts
from services.seed_service import SeedService
from services.auth_service import (
    create_session, get_session_user, clear_session,
    is_authenticated, is_admin, verify_password
)
from repositories.user_repository import UserRepository
import models

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Depot Jawara SES Forecasting API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
from config import get_settings
settings = get_settings()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    max_age=None,  # Browser session (closes when browser closes)
    same_site="lax",
)

# Setup templates and static files
# cache_size=0 works around a Python 3.14 weakref hashability bug in Jinja2's LRU cache
_jinja_env = Environment(loader=FileSystemLoader("templates"), cache_size=0)
templates = Jinja2Templates(env=_jinja_env)

# Custom Jinja filter for date formatting
def date_filter(value):
    """Format date/datetime/string to YYYY-MM-DD."""
    if value is None:
        return 'N/A'
    if isinstance(value, str):
        return value[:10] if len(value) >= 10 else value
    # datetime object
    return value.strftime('%Y-%m-%d')

templates.env.filters['date_format'] = date_filter

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers with /api prefix to avoid conflicts with template routes
app.include_router(auth.router, tags=["auth"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(forecasts.router, prefix="/api/forecast", tags=["forecasts"])


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/debug/session")
async def debug_session(request: Request):
    """Debug endpoint to check session state."""
    from services.auth_service import get_session_user, is_authenticated
    return {
        "is_authenticated": is_authenticated(request),
        "session_data": dict(request.session),
        "user": get_session_user(request),
        "cookies": request.cookies,
    }


# Startup event - seed initial data
@app.on_event("startup")
async def startup_event():
    """Seed initial data on application startup."""
    db: Session = next(get_db())
    try:
        seed_service = SeedService(db)
        seed_service.seed_all()
    finally:
        db.close()


# ============= TEMPLATE ROUTES =============

@app.get("/")
async def root(request: Request):
    """Root route - redirect to appropriate dashboard based on auth."""
    if is_authenticated(request):
        user = get_session_user(request)
        default = "dashboard" if user.get("role") == "admin" else "forecasts"
        return RedirectResponse(url=f"/{default}", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login")
async def login_page(request: Request):
    """Render login page."""
    if is_authenticated(request):
        user = get_session_user(request)
        default = "dashboard" if user.get("role") == "admin" else "forecasts"
        return RedirectResponse(url=f"/{default}", status_code=302)
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form submission."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    create_session(request, user.username, user.role)
    print(f"DEBUG login: session={dict(request.session)}, user={user.username}, role={user.role}")
    default = "dashboard" if user.role == "admin" else "forecasts"
    return RedirectResponse(url=f"/{default}", status_code=302)


@app.get("/logout")
async def logout(request: Request):
    """Logout and clear session."""
    clear_session(request)
    return RedirectResponse(url="/login", status_code=302)


# ============= LEGACY REDIRECTS (for bookmarked links) =============

@app.get("/admin")
@app.get("/admin/")
async def legacy_admin_redirect(request: Request):
    """Redirect old /admin links to new dashboard."""
    return RedirectResponse(url="/dashboard", status_code=301)


@app.get("/owner")
@app.get("/owner/")
async def legacy_owner_redirect(request: Request):
    """Redirect old /owner links to new dashboard."""
    return RedirectResponse(url="/forecasts", status_code=301)


# ============= DASHBOARD ROUTES =============

@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    if user.get("role") != "admin":
        return RedirectResponse(url="/forecasts", status_code=302)

    from repositories.product_repository import ProductRepository
    from repositories.sale_repository import SaleRepository
    from repositories.forecast_repository import ForecastRepository

    product_repo = ProductRepository(db)
    sale_repo = SaleRepository(db)
    forecast_repo = ForecastRepository(db)

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "total_products": product_repo.count(),
        "total_sales": sale_repo.count(),
        "total_forecasts": forecast_repo.count(),
        "recent_sales": sale_repo.get_recent(limit=10),
        "projects": forecast_repo.get_project_summaries()
    })


@app.get("/products")
async def products(request: Request, db: Session = Depends(get_db)):
    """Product management page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    if user.get("role") != "admin":
        return RedirectResponse(url="/forecasts", status_code=302)

    from repositories.product_repository import ProductRepository
    product_repo = ProductRepository(db)

    return templates.TemplateResponse(request, "products.html", {
        "user": user,
        "products": product_repo.get_all()
    })


@app.get("/sales")
async def sales(request: Request, db: Session = Depends(get_db)):
    """Sales management page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    if user.get("role") != "admin":
        return RedirectResponse(url="/forecasts", status_code=302)

    from repositories.product_repository import ProductRepository
    from repositories.sale_repository import SaleRepository
    product_repo = ProductRepository(db)
    sale_repo = SaleRepository(db)

    return templates.TemplateResponse(request, "sales.html", {
        "user": user,
        "products": product_repo.get_all(),
        "sales": sale_repo.get_all()
    })


@app.get("/forecast")
async def forecast(request: Request, db: Session = Depends(get_db)):
    """Forecast calculator page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    if user.get("role") != "admin":
        return RedirectResponse(url="/forecasts", status_code=302)

    from repositories.product_repository import ProductRepository
    product_repo = ProductRepository(db)

    return templates.TemplateResponse(request, "forecast.html", {
        "user": user,
        "products": product_repo.get_all()
    })


@app.get("/forecast/compare")
async def forecast_compare(request: Request, db: Session = Depends(get_db)):
    """Compare-all-alphas page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    if user.get("role") != "admin":
        return RedirectResponse(url="/forecasts", status_code=302)

    from repositories.product_repository import ProductRepository
    product_repo = ProductRepository(db)

    return templates.TemplateResponse(request, "forecast_compare.html", {
        "user": user,
        "products": product_repo.get_all()
    })


@app.get("/forecasts")
async def forecasts(request: Request, db: Session = Depends(get_db)):
    """View forecasts page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    from repositories.forecast_repository import ForecastRepository
    forecast_repo = ForecastRepository(db)

    return templates.TemplateResponse(request, "forecasts.html", {
        "user": user,
        "latest_forecasts": forecast_repo.get_latest(),
        "projects": forecast_repo.get_project_summaries(),
        "total_forecasts": forecast_repo.count()
    })


@app.get("/chart")
async def chart(request: Request, db: Session = Depends(get_db)):
    """Forecast chart page."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)

    user = get_session_user(request)
    from repositories.forecast_repository import ForecastRepository
    import json

    forecast_repo = ForecastRepository(db)

    # Get latest forecasts and convert to dict for JSON serialization
    latest = forecast_repo.get_all_ordered()
    latest_dicts = []
    for f in latest:
        # Parse calculation_steps - might be JSON string or dict
        steps_data = f.calculation_steps
        if isinstance(steps_data, str):
            steps_data = json.loads(steps_data)

        steps = steps_data.get("steps", []) if isinstance(steps_data, dict) else (steps_data if isinstance(steps_data, list) else [])

        dates = [step.get("date") for step in steps]
        actuals = [step.get("actual") for step in steps]
        forecasts = [step.get("forecast") for step in steps]

        latest_dicts.append({
            "id": f.id,
            "project_name": f.project_name,
            "product_name": f.product_name,
            "next_period_forecast": f.next_period_forecast,
            "next_period_date": f.next_period_date.isoformat() if f.next_period_date else None,
            "alpha": f.alpha,
            "mape": f.mape,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "dates": dates,
            "actuals": actuals,
            "forecasts": forecasts
        })

    return templates.TemplateResponse(request, "chart.html", {
        "user": user,
        "latest_forecasts": latest_dicts,
        "projects": forecast_repo.get_project_summaries()
    })


