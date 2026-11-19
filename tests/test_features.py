"""Lags and targets must follow calendar days and only use information available at forecast time."""
import numpy as np
import pandas as pd

from src.features import add_features


def _daily(values, dates):
    return pd.DataFrame({"station": "a", "date": pd.to_datetime(dates), "pm25": values,
                         "temp": 1.0, "rh": 1.0, "wind_speed": 1.0, "wind_sin": 0.0,
                         "wind_cos": 1.0, "rain": 0.0})


def test_lag_and_target_use_calendar_days():
    out = add_features(_daily([10.0, 20.0, 30.0, 40.0], ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"]))
    third = out[out["date"] == "2025-01-03"].iloc[0]
    assert third["pm25_lag1"] == 20.0 and third["pm25_lag2"] == 10.0
    assert third["target_pm25_h1"] == 40.0


def test_missing_day_is_not_skipped():
    out = add_features(_daily([10.0, 30.0], ["2025-01-01", "2025-01-03"]))  # 2 Jan absent
    third = out[out["date"] == "2025-01-03"].iloc[0]
    assert np.isnan(third["pm25_lag1"])  # yesterday is unknown, not 1 Jan
    assert third["pm25_lag2"] == 10.0


def test_rolling_mean_uses_only_past_and_today():
    out = add_features(_daily([10.0, 20.0, 30.0, 1000.0], ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"]))
    third = out[out["date"] == "2025-01-03"].iloc[0]
    assert third["pm25_roll3"] == 20.0  # (10 + 20 + 30) / 3, ignores 4 Jan
