# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack **Single Exponential Smoothing (SES) Forecasting Application** for "Depot Jawara". Backend: Python FastAPI + SQLAlchemy. Frontend: Jinja2 HTML templates + Tailwind CSS served by FastAPI. Auth: dual-mode (JWT for API, session cookies for web UI).

## Development Commands

```bash
pip install -r requirements.txt
uvicorn main:app --reload          # dev server on port 8000
pytest                             # run all tests
pytest tests/test_api/test_forecasts_api.py::TestForecastsAPI::test_create_forecast_admin  # single test
pytest --cov=. --cov-report=html   # with coverage
python migrate_to_mysql.py         # SQLite → MySQL migration
docker-compose up -d               # production (MySQL + backend)
```

Default accounts (auto-created on first start): `admin`/`admin123`, `owner`/`owner123`.

## Architecture

### Layers

| Layer | Location | Role |
|-------|----------|------|
| API | `api/` | FastAPI routers, request/response |
| Service | `services/` | Business logic, SES calc, auth |
| Repository | `repositories/` | DB queries via SQLAlchemy |
| Schema | `schemas/` | Pydantic validation models |
| Model | `models.py` | SQLAlchemy ORM |

### Key files
- `main.py` — app init, all web UI template routes, session middleware
- `database.py` — engine setup, auto-detects SQLite vs MySQL
- `config.py` — Pydantic settings, reads `.env`
- `services/auth_service.py` — JWT + session auth helpers
- `services/forecast_service.py` — `calculate_ses_with_steps()` core algorithm
- `services/seed_service.py` — seeds users, products, sales on empty DB at startup

### Frontend conventions
- All pages extend `templates/base.html`, include `templates/partials/sidebar.html`
- `static/js/api.js` — global `api` object (fetch wrapper with session cookies). Use `api.get()`, `api.post()`, `api.put()`, `api.delete()`.
- Tables that need sorting/pagination use **DataTables 1.13.8** (jQuery-dependent). Load jQuery before DataTables in `{% block scripts %}`.
- Admin-only pages redirect owner → `/forecasts`. Unauthenticated → `/login`.

## Role-Based Access

- **Admin:** dashboard, products, sales, forecast (create), forecasts (view), chart
- **Owner:** forecasts (view), chart
- API: `get_current_user_or_session` (any auth), `get_admin_user_or_session` (admin only, 403 for owner)

## Core Algorithm

`services/forecast_service.py` → `calculate_ses_with_steps(actuals, dates, alpha)`

**Formula:** `F(t+1) = α × A(t) + (1-α) × F(t)`, initialized with `F1 = A1`

Returns: forecasts list, step-by-step detail, MAPE. Results saved to `Forecasts` table on every `POST /api/forecast`.

## Database Schema

```
Users:     id, username, hashed_password, role ('admin'|'owner')
Products:  id, name, created_at
Sales:     id, date (Date), product_name, qty
Forecasts: id, project_name, created_at, created_by, alpha,
           product_name, next_period_forecast, next_period_date,
           mape, calculation_steps (JSON)
```

`Sales.date` is a SQLAlchemy `Date` column. When comparing with strings in queries, pass ISO format `YYYY-MM-DD` — works for both SQLite and MySQL.

## API Endpoints

**Auth:** `POST /token`, `GET /users/me`

**Sales:** `GET /api/sales?product_name=&date_from=&date_to=`, `POST /api/sales`, `DELETE /api/sales/{id}`

**Products:** `GET /api/products`, `POST /api/products`, `DELETE /api/products/{id}`

**Forecasts:** `POST /api/forecast`, `GET /api/forecast/latest`, `GET /api/forecasts/history`, `GET /api/forecast/projects`, `GET /api/forecast/project/{project_name}`

**Web UI:** `/`, `/login`, `/logout`, `/dashboard`, `/products`, `/sales`, `/forecast`, `/forecasts`, `/chart`

## Authentication Detail

**Session (web UI):** cookie via Starlette `SessionMiddleware`. Helpers in `services/auth_service.py`: `create_session()`, `get_session_user()`, `is_authenticated()`, `is_admin()`. All template routes in `main.py` check `is_authenticated()` first.

**JWT (API):** Bearer token, validated via `get_current_user()` in `api/auth.py`. Frontend stores token in `localStorage` (used by `api.js`).

## Testing

In-memory SQLite, function-scoped `db_session` fixture. Test structure:
- `tests/conftest.py` — fixtures: `db_session`, `client`, `test_users`, `admin_token`, `owner_token`, `auth_headers`, `test_products`, `test_sales`
- `tests/test_api/` — endpoint tests grouped by resource
- `tests/test_*_service.py` — service unit tests

## Environment

```bash
DATABASE_URL=mysql+pymysql://user:pass@host:3306/sales_app  # omit for SQLite default
SECRET_KEY=random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
