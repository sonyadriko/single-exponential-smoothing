from main import calculate_ses, calculate_mape
import numpy as np

def test_ses():
    # Simple case
    # Series: [10, 10, 10], Alpha: 0.5
    # F0 = 10
    # F1 = 0.5*10 + 0.5*10 = 10
    # F2 = 0.5*10 + 0.5*10 = 10
    series = [10.0, 10.0, 10.0]
    result = calculate_ses(series, 0.5)
    print(f"Expect [10, 10, 10], Got: {result}")
    assert result == [10.0, 10.0, 10.0]

    # Increasing series
    # Series: [10, 20, 30], Alpha: 0.5
    # F0 = 10
    # F1 = 0.5*10 + 0.5*10 = 10 # PREV actual was 10, PREV forecast was 10. Wait.
    # Logic in main.py:
    # result = [series[0]] -> [10]
    # i=1 (Value 20): prev_forecast=10, prev_actual=10. next = 0.5*10 + 0.5*10 = 10.
    # i=2 (Value 30): prev_forecast=10, prev_actual=20. next = 0.5*20 + 0.5*10 = 15.
    series2 = [10.0, 20.0, 30.0]
    result2 = calculate_ses(series2, 0.5)
    print(f"Expect [10, 10, 15], Got: {result2}")
    assert result2 == [10.0, 10.0, 15.0]

    print("SES Tests Passed!")

if __name__ == "__main__":
    test_ses()
