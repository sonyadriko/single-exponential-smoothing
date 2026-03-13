from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ForecastRequest(BaseModel):
    alpha: float
    product_name: Optional[str] = None
    project_name: Optional[str] = None
    next_period_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CalculationStep(BaseModel):
    period: int
    date: str
    actual: float
    forecast: float
    formula: str
    calculation: str
    result: float
    error: float
    error_pct: float


class ForecastCreate(BaseModel):
    project_name: Optional[str] = None
    created_at: str
    created_by: int
    alpha: float
    product_name: str
    next_period_forecast: float
    next_period_date: Optional[str] = None
    mape: float
    calculation_steps: Dict[str, Any]


class ForecastResponse(BaseModel):
    id: int
    created_at: str
    alpha: float
    product_name: str
    next_period_forecast: float
    next_period_date: Optional[str] = None
    mape: float
    dates: List[str]
    actuals: List[float]
    forecasts: List[float]
    steps: List[Dict[str, Any]]


class ForecastOut(BaseModel):
    id: int
    created_at: str
    alpha: float
    product_name: str
    next_period_forecast: float
    next_period_date: Optional[str] = None
    mape: float


class ForecastResult(BaseModel):
    dates: List[str]
    actuals: List[float]
    forecasts: List[float]
    steps: List[Dict[str, Any]]
    mape: float
    next_period_forecast: float
    next_period_date: Optional[str] = None


class ForecastCreateResponse(BaseModel):
    results: Dict[str, ForecastResult]
    overall_mape: float
    created_at: str


class ForecastProjectInfo(BaseModel):
    project_name: str
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    alpha: float
    forecast_count: int
    overall_mape: float


class ForecastProjectDetail(BaseModel):
    project_name: str
    created_at: str
    alpha: float
    results: Dict[str, ForecastResult]
    overall_mape: float
