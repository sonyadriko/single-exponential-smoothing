from typing import List, Dict, Any
import numpy as np


def calculate_ses_with_steps(series: List[float], dates: List[str], alpha: float) -> Dict[str, Any]:
    """
    Calculate Single Exponential Smoothing (SES) with detailed step-by-step calculations.

    Formula: F(t) = alpha × A(t) + (1-alpha) × F(t-1)

    Each row's forecast folds in that same period's actual value (matches the
    reference Excel workbook), so F(t) also serves directly as the forecast
    for period t+1 — no separate lookahead step is needed.

    Args:
        series: List of actual values
        dates: List of date strings corresponding to each value
        alpha: Smoothing coefficient (0-1)

    Returns:
        Dictionary with forecasts, steps, and MAPE
    """
    if not series:
        return {"forecasts": [], "steps": [], "mape": 0}

    forecasts = [series[0]]
    steps = []

    # Step 1: Initial forecast
    steps.append({
        "period": 1,
        "date": dates[0] if dates else "N/A",
        "actual": series[0],
        "forecast": series[0],
        "formula": "F₁ = A₁ (Initial)",
        "calculation": f"F₁ = {series[0]}",
        "result": series[0],
        "error": 0,
        "error_pct": 0
    })

    # Subsequent steps
    for i in range(1, len(series)):
        current_actual = series[i]
        prev_forecast = forecasts[i - 1]

        # Calculate forecast (folds in this period's own actual)
        current_forecast = alpha * current_actual + (1 - alpha) * prev_forecast
        forecasts.append(current_forecast)

        # Calculate error
        error = abs(current_actual - current_forecast)
        error_pct = (error / current_actual * 100) if current_actual != 0 else 0

        steps.append({
            "period": i + 1,
            "date": dates[i] if dates and i < len(dates) else "N/A",
            "actual": current_actual,
            "forecast": current_forecast,
            "formula": f"F{i+1} = {alpha} × A{i+1} + (1-{alpha}) × F{i}",
            "calculation": f"F{i+1} = {alpha} × {current_actual} + {1-alpha} × {prev_forecast}",
            "result": current_forecast,
            "error": error,
            "error_pct": error_pct
        })

    return {
        "forecasts": forecasts,
        # First period has no real forecast error (F1 = A1 by definition), so it's excluded from MAPE
        "mape": calculate_mape(series[1:], forecasts[1:]),
        "steps": steps
    }


def calculate_mape(actual: List[float], forecast: List[float]) -> float:
    """
    Calculate Mean Absolute Percentage Error (MAPE).

    Args:
        actual: List of actual values
        forecast: List of forecasted values

    Returns:
        MAPE as a percentage
    """
    actual_np = np.array(actual)
    forecast_np = np.array(forecast)
    mask = actual_np != 0
    if not np.any(mask):
        return 0
    return float(np.mean(np.abs((actual_np[mask] - forecast_np[mask]) / actual_np[mask])) * 100)


def compare_alphas(series: List[float], dates: List[str], alphas: List[float]) -> Dict[str, Any]:
    """
    Run SES for multiple alpha values on the same series and compare MAPE.

    Args:
        series: List of actual values
        dates: List of date strings corresponding to each value
        alphas: List of smoothing coefficients to compare

    Returns:
        Dictionary with per-alpha forecasts/MAPE/next-period forecast and the best alpha
    """
    by_alpha: Dict[str, Any] = {}

    for alpha in alphas:
        calc_result = calculate_ses_with_steps(series, dates, alpha)
        forecasts = calc_result["forecasts"]
        next_forecast = forecasts[-1] if forecasts else 0

        by_alpha[f"{alpha:.1f}"] = {
            "alpha": alpha,
            "forecasts": forecasts,
            "error_pct": [step["error_pct"] for step in calc_result["steps"]],
            "mape": calc_result["mape"],
            "next_period_forecast": next_forecast
        }

    best_key = min(by_alpha, key=lambda k: by_alpha[k]["mape"]) if by_alpha else None

    return {
        "dates": dates,
        "actuals": series,
        "by_alpha": by_alpha,
        "best_alpha": by_alpha[best_key]["alpha"] if best_key else None
    }


def calculate_next_period_forecast(last_actual: float, last_forecast: float, alpha: float) -> float:
    """
    Calculate the forecast for the next period.

    Args:
        last_actual: The last actual value
        last_forecast: The last forecast value
        alpha: Smoothing coefficient

    Returns:
        Next period forecast
    """
    return alpha * last_actual + (1 - alpha) * last_forecast
