import pytest
from services.forecast_service import calculate_ses_with_steps, calculate_mape, calculate_next_period_forecast


class TestCalculateSES:
    """Test Single Exponential Smoothing calculations."""

    def test_constant_series(self):
        """Test SES with a constant series."""
        series = [10.0, 10.0, 10.0]
        dates = ["2025-05-01", "2025-05-02", "2025-05-03"]
        result = calculate_ses_with_steps(series, dates, 0.5)

        assert result["forecasts"] == [10.0, 10.0, 10.0]
        assert len(result["steps"]) == 3
        assert result["mape"] == 0

    def test_increasing_series(self):
        """Test SES with an increasing series."""
        series = [10.0, 20.0, 30.0]
        dates = ["2025-05-01", "2025-05-02", "2025-05-03"]
        result = calculate_ses_with_steps(series, dates, 0.5)

        # F1 = A1 = 10
        # F2 = 0.5 * 10 + 0.5 * 10 = 10
        # F3 = 0.5 * 20 + 0.5 * 10 = 15
        assert result["forecasts"][0] == 10.0
        assert result["forecasts"][1] == 10.0
        assert result["forecasts"][2] == 15.0

    def test_different_alpha(self):
        """Test SES with different alpha values."""
        series = [10.0, 20.0, 30.0]
        dates = ["2025-05-01", "2025-05-02", "2025-05-03"]

        # Alpha = 1.0 (full weight to actual)
        result_alpha_1 = calculate_ses_with_steps(series, dates, 1.0)
        # F1 = 10, F2 = 20, F3 = 30
        assert result_alpha_1["forecasts"][1] == 10.0
        assert result_alpha_1["forecasts"][2] == 20.0

        # Alpha = 0.0 (full weight to forecast)
        result_alpha_0 = calculate_ses_with_steps(series, dates, 0.0)
        # F1 = 10, F2 = 10, F3 = 10
        assert result_alpha_0["forecasts"][1] == 10.0
        assert result_alpha_0["forecasts"][2] == 10.0

    def test_empty_series(self):
        """Test SES with an empty series."""
        result = calculate_ses_with_steps([], [], 0.5)
        assert result["forecasts"] == []
        assert result["steps"] == []
        assert result["mape"] == 0

    def test_steps_structure(self):
        """Test that steps contain all required fields."""
        series = [10.0, 20.0]
        dates = ["2025-05-01", "2025-05-02"]
        result = calculate_ses_with_steps(series, dates, 0.5)

        step = result["steps"][1]  # Second step
        assert "period" in step
        assert "date" in step
        assert "actual" in step
        assert "forecast" in step
        assert "formula" in step
        assert "calculation" in step
        assert "result" in step
        assert "error" in step
        assert "error_pct" in step


class TestCalculateMAPE:
    """Test MAPE calculation."""

    def test_perfect_forecast(self):
        """Test MAPE with perfect forecast (0%)."""
        actual = [10.0, 20.0, 30.0]
        forecast = [10.0, 20.0, 30.0]
        mape = calculate_mape(actual, forecast)
        assert mape == 0

    def test_some_error(self):
        """Test MAPE with forecast error."""
        actual = [100.0, 100.0, 100.0]
        forecast = [90.0, 110.0, 100.0]
        mape = calculate_mape(actual, forecast)
        # Average of (10%, 10%, 0%) = 6.67%
        assert abs(mape - 6.67) < 0.1

    def test_zero_values(self):
        """Test MAPE with zero values (should handle gracefully)."""
        actual = [0.0, 10.0, 20.0]
        forecast = [5.0, 12.0, 18.0]
        mape = calculate_mape(actual, forecast)
        # Should ignore zero values
        assert mape > 0


class TestNextPeriodForecast:
    """Test next period forecast calculation."""

    def test_basic_calculation(self):
        """Test basic next period forecast."""
        result = calculate_next_period_forecast(100, 90, 0.5)
        # 0.5 * 100 + 0.5 * 90 = 95
        assert result == 95.0

    def test_alpha_one(self):
        """Test with alpha = 1 (full weight to actual)."""
        result = calculate_next_period_forecast(100, 90, 1.0)
        # 1.0 * 100 + 0 * 90 = 100
        assert result == 100.0

    def test_alpha_zero(self):
        """Test with alpha = 0 (full weight to forecast)."""
        result = calculate_next_period_forecast(100, 90, 0.0)
        # 0 * 100 + 1.0 * 90 = 90
        assert result == 90.0
