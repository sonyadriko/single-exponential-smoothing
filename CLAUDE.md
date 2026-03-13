# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack **Single Exponential Smoothing (SES) Forecasting Application** for "Depot Jawara". The application provides sales forecasting capabilities using time series analysis with an interactive UI for calculating, visualizing, and managing forecasts.

## Architecture

**Backend:** Python FastAPI + SQLAlchemy + SQLite
**Frontend:** HTML templates with Tailwind CSS (served via FastAPI)

### Project Structure

- `main.py` - Main FastAPI application with all routes, authentication, and SES calculation logic
- `models.py` - SQLAlchemy ORM models (User, Product, Sale, Forecast)
- `database.py` - SQLite database configuration and session management
- `config.py` - Application configuration
- `migrate_db.py` - Database migration utilities
- `sales_app.db` - SQLite database (auto-created on first run)
- `api/` - API route modules (auth, forecasts, products, sales)
- `repositories/` - Data access layer
- `schemas/` - Pydantic schemas for request/response validation
- `services/` - Business logic layer
- `static/` - Static assets (CSS, JS)
- `templates/` - HTML templates for web UI
- `tests/` - Test files

**Key endpoints:**
- Auth: `/token` (login), `/users/me` (current user)
- Sales: `GET/POST /sales`, `/sales/product/{product_name}`
- Products: `GET/POST /products`, `DELETE /products/{product_id}`
- Forecasts: `POST /forecast`, `GET /forecast/latest`, `GET /forecasts/history`
- Forecast Projects: `/forecast/projects`, `/forecast/project/{project_name}`
- Admin-only: User/forecast project management, data reset (`/reset-data`)
- Web UI: `/`, `/login`, `/admin`, `/owner`, `/sales`

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start dev server (port 8000)
uvicorn main:app --reload

# Run tests
pytest tests/

# Database migration
python migrate_db.py
```

### Default Test Accounts
- **Admin:** `admin` / `admin123` (full access)
- **Owner:** `owner` / `owner123` (view forecasts, no admin operations)

These are auto-created on first server start via the `startup_event()` handler in `main.py`.

## Core Algorithm: Single Exponential Smoothing (SES)

Located in `main.py` (`calculate_ses_with_steps` function in services/forecast_service.py).

**Formula:** `F(t+1) = alpha × A(t) + (1-alpha) × F(t)`
- `F(t+1)` = forecast for next period
- `A(t)` = actual value in current period
- `F(t)` = forecast for current period
- `alpha` = smoothing coefficient (0-1)

**Initialization:** `F1 = A1` (first forecast equals first actual value)

**MAPE Calculation:** Mean Absolute Percentage Error for forecast accuracy

The function returns detailed step-by-step calculations including period, date, actual, forecast, formula, calculation, error, and error percentage.

## Database Schema (SQLite)

**Users:** id, username, hashed_password, role ('admin' | 'owner')
**Products:** id, name, created_at
**Sales:** id, date, product_name, qty
**Forecasts:** id, project_name, created_at, created_by, alpha, product_name, next_period_forecast, mape, calculation_steps (JSON)

## Key Implementation Details

1. **Authentication:** JWT tokens stored in `localStorage`. Token includes `username` and `role` claims. Validated via `get_current_user()` dependency.

2. **Role-Based Access:**
   - `get_current_user()` - Any authenticated user
   - `get_admin_user()` - Admin-only endpoints (returns 403 for owners)

3. **CORS:** Currently allows all origins (`allow_origins=["*"]`). Should be restricted in production.

4. **Seed Data:** On startup, creates default users, 8 products (Indonesian food items), and May 2025 sales data if tables are empty.

5. **Forecast Projects:** A "project" is a collection of forecasts (one per product) created at the same time with the same alpha parameter, identified by a `project_name`.

## Production Considerations

- `SECRET_KEY` should be set via environment variable (see `.env.example`)
- CORS allows all origins - should restrict in production
- SQLite suitable for development; consider PostgreSQL or MySQL for production
- No HTTPS enforcement - add in production deployment
- Use Docker with the provided `Dockerfile` and `docker-compose.yml` for containerized deployment
