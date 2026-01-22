from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Depot Jawara SES Forecasting")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataPoint(BaseModel):
    date: str
    product_name: str
    qty: int

class ForecastRequest(BaseModel):
    data: List[DataPoint]
    alpha: float

class ForecastResponse(BaseModel):
    results: Dict[str, Any] # Keyed by product name
    overall_mape: float

def calculate_ses(series: List[float], alpha: float) -> List[float]:
    result = [series[0]] # Initialize first forecast with first actual
    for i in range(1, len(series)):
        prev_forecast = result[-1]
        prev_actual = series[i-1]
        next_forecast = alpha * prev_actual + (1 - alpha) * prev_forecast
        result.append(next_forecast)
    return result

def calculate_mape(actual: List[float], forecast: List[float]) -> float:
    actual_np = np.array(actual)
    forecast_np = np.array(forecast)
    
    # Avoid division by zero
    mask = actual_np != 0
    return np.mean(np.abs((actual_np[mask] - forecast_np[mask]) / actual_np[mask])) * 100

@app.post("/forecast")
async def get_forecast(request: ForecastRequest):
    df = pd.DataFrame([d.dict() for d in request.data])
    
    if df.empty:
        raise HTTPException(status_code=400, detail="No data provided")

    results = {}
    total_mape = 0
    product_count = 0

    # Group by product
    for product_name, group in df.groupby("product_name"):
        group = group.sort_values("date")
        actuals = group["qty"].tolist()
        dates = group["date"].tolist()
        
        if not actuals:
            continue
            
        forecasts = calculate_ses(actuals, request.alpha)
        mape = calculate_mape(actuals, forecasts)
        
        # Predict next period (June 1st roughly, or just next step)
        next_forecast = request.alpha * actuals[-1] + (1 - request.alpha) * forecasts[-1]
        
        results[product_name] = {
            "dates": dates,
            "actuals": actuals,
            "forecasts": forecasts,
            "mape": mape,
            "next_period_forecast": next_forecast
        }
        
        total_mape += mape
        product_count += 1

    overall_mape = total_mape / product_count if product_count > 0 else 0

    return {
        "results": results,
        "overall_mape": overall_mape
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
