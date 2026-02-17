# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack **Single Exponential Smoothing (SES) Forecasting Application** for "Depot Jawara". The application provides sales forecasting capabilities using time series analysis with an interactive UI for calculating, visualizing, and managing forecasts.

## Architecture

**Frontend:** React 19.2 + TypeScript + Vite + Tailwind CSS
**Backend:** Python FastAPI + SQLAlchemy + SQLite
**API Communication:** Axios with JWT authentication

The project follows a traditional monorepo structure with separate `frontend/` and `backend/` directories.

### Backend Structure (FastAPI)

- `main.py` - Single-file API containing all routes, authentication, and SES calculation logic
- `models.py` - SQLAlchemy ORM models (User, Product, Sale, Forecast)
- `database.py` - SQLite database configuration and session management
- `test_logic.py` - Unit tests for SES calculation formulas
- `sales_app.db` - SQLite database (auto-created on first run)

**Key endpoints:**
- Auth: `/token` (login), `/users/me` (current user)
- Sales: `GET/POST /sales`, `/sales/product/{product_name}`
- Products: `GET/POST /products`, `DELETE /products/{product_id}`
- Forecasts: `POST /forecast`, `GET /forecast/latest`, `GET /forecasts/history`
- Forecast Projects: `/forecast/projects`, `/forecast/project/{project_name}`
- Admin-only: User/forecast project management, data reset (`/reset-data`)

### Frontend Structure (React)

- `src/App.tsx` - Main routing with React Router (protected routes for `/admin` and `/owner`)
- `src/components/` - All UI components (no pages directory)
  - `Login.tsx` - Authentication form
  - `AdminDashboard.tsx` - Admin interface (user/product/sales management)
  - `OwnerDashboard.tsx` - Standard user dashboard (forecast viewing)
  - `ForecastCalculator.tsx` - Interactive SES calculation with adjustable alpha
  - `ForecastChart.tsx` - Recharts visualization
  - `ForecastProjectManager.tsx` - CRUD for forecast projects
  - `SalesInput.tsx` - Historical sales data entry
  - `ProductManager.tsx` - Product catalog management

**API base URL:** Hardcoded as `http://127.0.0.1:8000` throughout components

## Development Commands

### Frontend (from `/frontend`)
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (Vite on port 5173)
npm run build        # TypeScript check + production build
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Backend (from `/backend`)
```bash
pip install -r requirements.txt    # Install Python dependencies
uvicorn main:app --reload          # Start dev server (port 8000)
python test_logic.py               # Run SES calculation unit tests
```

### Default Test Accounts
- **Admin:** `admin` / `admin123` (full access)
- **Owner:** `owner` / `owner123` (view forecasts, no admin operations)

These are auto-created on first server start via the `startup_event()` handler in `main.py:144`.

## Core Algorithm: Single Exponential Smoothing (SES)

Located in `backend/main.py:220` (`calculate_ses_with_steps` function).

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

## Frontend Configuration

- **Vite:** `vite.config.ts` with `@vitejs/plugin-react`
- **Tailwind:** `tailwind.config.js` with custom theme colors
- **TypeScript:** `tsconfig.json` (via Vite plugin)
- **ESLint:** `eslint.config.js` with React Hooks and React Refresh plugins

## Production Considerations

- `SECRET_KEY` is hardcoded in `main.py:31` - should be environment variable
- CORS allows all origins - should restrict to frontend domain
- SQLite suitable for development; consider PostgreSQL for production
- No HTTPS enforcement - add in production deployment
