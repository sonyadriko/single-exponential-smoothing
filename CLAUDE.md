# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack **Single Exponential Smoothing (SES) Forecasting Application** for "Depot Jawara". The application provides sales forecasting capabilities using time series analysis with an interactive UI for calculating, visualizing, and managing forecasts.

## Architecture

**Backend:** Python FastAPI + SQLAlchemy (SQLite for dev, MySQL for production)
**Frontend:** HTML templates with Tailwind CSS (served via FastAPI)
**Authentication:** Dual-mode - JWT tokens for API, session-based for web UI

### Layered Architecture

The codebase follows a clean layered architecture:

- **API Layer** (`api/`) - FastAPI route handlers, request/response handling
- **Service Layer** (`services/`) - Business logic, SES calculations, authentication
- **Repository Layer** (`repositories/`) - Data access, database queries
- **Schema Layer** (`schemas/`) - Pydantic models for validation
- **Model Layer** (`models.py`) - SQLAlchemy ORM models

### Key Files

- `main.py` - FastAPI app initialization, middleware setup, template routes
- `database.py` - Database engine and session management (supports SQLite/MySQL)
- `config.py` - Pydantic settings with `.env` support
- `services/auth_service.py` - Dual authentication (JWT + session-based)
- `services/forecast_service.py` - SES calculation algorithm
- `services/seed_service.py` - Initial data seeding on startup
- `migrate_to_mysql.py` - SQLite to MySQL migration with date format conversion

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start dev server (port 8000)
uvicorn main:app --reload

# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api/test_forecasts_api.py

# Run specific test class or method
pytest tests/test_api/test_forecasts_api.py::TestForecastsAPI::test_create_forecast_admin

# Run tests in verbose mode
pytest -v

# Database migration (SQLite to MySQL)
python migrate_to_mysql.py

# Docker deployment
docker-compose up -d
docker-compose logs -f backend
docker-compose down
```

### Default Test Accounts
- **Admin:** `admin` / `admin123` (full access - create forecasts, manage users)
- **Owner:** `owner` / `owner123` (read-only - view forecasts only)

These are auto-created on first server start via the `startup_event()` handler in `main.py`.

## Core Algorithm: Single Exponential Smoothing (SES)

Located in `services/forecast_service.py` (`calculate_ses_with_steps` function).

**Formula:** `F(t+1) = alpha × A(t) + (1-alpha) × F(t)`
- `F(t+1)` = forecast for next period
- `A(t)` = actual value in current period
- `F(t)` = forecast for current period
- `alpha` = smoothing coefficient (0-1)

**Initialization:** `F1 = A1` (first forecast equals first actual value)

**MAPE Calculation:** Mean Absolute Percentage Error for forecast accuracy

The function returns detailed step-by-step calculations including period, date, actual, forecast, formula, calculation, error, and error percentage.

## Database Schema

**Users:** id, username, hashed_password, role ('admin' | 'owner')
**Products:** id, name, created_at
**Sales:** id, date, product_name, qty
**Forecasts:** id, project_name, created_at, created_by, alpha, product_name, next_period_forecast, next_period_date, mape, calculation_steps (JSON)

## API Endpoints

**Authentication:**
- `POST /token` - Login (form data: username, password) → returns JWT token
- `GET /users/me` - Get current authenticated user

**Sales:**
- `GET /api/sales` - List all sales (with optional date filters)
- `POST /api/sales` - Create new sale (admin only)
- `GET /api/sales/product/{product_name}` - Get sales for specific product

**Products:**
- `GET /api/products` - List all products
- `POST /api/products` - Create new product (admin only)
- `DELETE /api/products/{product_id}` - Delete product (admin only)

**Forecasts:**
- `POST /api/forecast` - Create forecast(s) (admin only)
- `GET /api/forecast/latest` - Get latest forecast
- `GET /api/forecasts/history` - Get forecast history
- `GET /api/forecast/projects` - List all forecast projects
- `GET /api/forecast/project/{project_name}` - Get forecasts by project name

**Web UI Routes:**
- `GET /` - Home page (requires session auth)
- `GET /login` - Login page
- `POST /login` - Login form handler
- `GET /logout` - Logout handler
- `GET /admin` - Admin dashboard (admin only)
- `GET /owner` - Owner dashboard (owner only)
- `GET /sales` - Sales input page

## Key Implementation Details

### Authentication (Dual-Mode)

The app supports both JWT and session-based authentication:

**JWT Authentication** (API endpoints):
- Token stored in `localStorage` on frontend
- Token includes `username` and `role` claims
- Validated via `get_current_user()` dependency in `api/auth.py`
- Token creation/validation in `services/auth_service.py`

**Session Authentication** (Web UI):
- Session middleware with cookie-based sessions
- Functions: `create_session()`, `get_session_user()`, `clear_session()`, `is_authenticated()`, `is_admin()`
- Used by template routes in `main.py`

### Role-Based Access Control

- **Admin role:** Full access - create forecasts, manage users, reset data
- **Owner role:** Read-only - view forecasts and sales data only
- API dependencies: `get_current_user()` (any authenticated), `get_admin_user()` (admin only, returns 403 for owners)

### Database Configuration

- **Development:** SQLite (`sqlite:///./sales_app.db`) - default, auto-created
- **Production:** MySQL via `DATABASE_URL` environment variable
- Database engine auto-detects SQLite vs MySQL and applies appropriate connection settings
- Migration script (`migrate_to_mysql.py`) handles SQLite → MySQL migration with date format conversion

### Seed Data

On startup (`startup_event()` in `main.py`), creates if tables are empty:
- Default admin and owner users
- 8 products (Indonesian food items: Mie Instan, Beras, Gula Pasir, Minyak Goreng, Telur Ayam, Susu UHT, Kopi Sachet, Teh Celup)
- Sample sales data for May 2025

### Forecast Projects

A "project" is a collection of forecasts (one per product) created at the same time with the same alpha parameter, identified by a `project_name`. This allows grouping related forecasts for comparison and analysis.

## Testing

Tests use pytest with in-memory SQLite database for isolation.

**Test Structure:**
- `tests/conftest.py` - Shared fixtures (db_session, client, test_users, auth tokens, test data)
- `tests/test_api/` - API endpoint tests organized by resource
- `tests/test_*_service.py` - Service layer unit tests

**Key Fixtures:**
- `db_session` - In-memory SQLite database session (function-scoped)
- `client` - TestClient with database override
- `test_users` - Creates admin and owner test users
- `admin_token` / `owner_token` - JWT tokens for authenticated requests
- `auth_headers` - Pre-formatted Authorization headers
- `test_products` / `test_sales` - Sample data for testing

**Test Patterns:**
- Each test class groups related endpoint tests
- Tests verify both success cases and authorization (admin vs owner)
- Use `assert response.status_code == 200` pattern
- API tests use Bearer token authentication via headers

## Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sales_app
SECRET_KEY=change-this-to-a-random-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**For SQLite (development):** Set `DATABASE_URL=sqlite:///./sales_app.db` or omit to use default.

## Docker Deployment

The `docker-compose.yml` sets up MySQL + FastAPI backend:

- **MySQL container:** Port 3306, with health checks
- **Backend container:** Port 8000, waits for MySQL to be healthy
- Environment variables injected via docker-compose
- Volume for MySQL data persistence

## Production Considerations

- `SECRET_KEY` must be set to a secure random value via environment variable
- CORS currently allows all origins (`allow_origins=["*"]`) - restrict to specific domains in production
- SQLite suitable for development; use MySQL for production (migration script provided)
- Add HTTPS/TLS termination (nginx reverse proxy or cloud load balancer)
- Session middleware uses browser session cookies (closes when browser closes)
