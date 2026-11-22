"""Lag, rolling, weather and calendar features plus forecast targets (Module 2)."""
import numpy as np
import pandas as pd

from src.config import HORIZONS

FEATURE_COLS = [
    "pm25", "pm25_lag1", "pm25_lag2", "pm25_lag3", "pm25_roll3", "pm25_roll7",
    "temp", "rh", "wind_speed", "wind_sin", "wind_cos", "rain",
    "month_sin", "month_cos", "dayofweek", "season_flag",
]


def target_col(horizon):
    return f"target_pm25_h{horizon}"


def add_features(daily):
    """Build the modelling table. Each station is first given a complete daily calendar,
    so a lag of 1 always means 'yesterday', even when a day is missing."""
    tables = []
    for station, group in daily.groupby("station"):
        g = group.set_index("date").sort_index().asfreq("D")
        g["station"] = station
        for k in (1, 2, 3):
            g[f"pm25_lag{k}"] = g["pm25"].shift(k)
        g["pm25_roll3"] = g["pm25"].rolling(3, min_periods=2).mean()
        g["pm25_roll7"] = g["pm25"].rolling(7, min_periods=4).mean()
        month = g.index.month
        g["month_sin"] = np.sin(2 * np.pi * month / 12)
        g["month_cos"] = np.cos(2 * np.pi * month / 12)
        g["month"] = month
        g["dayofweek"] = g.index.dayofweek
        # Month-based stand-in for stubble-burning season (no fire data yet): Oct-Feb
        g["season_flag"] = pd.Series(month, index=g.index).isin([10, 11, 12, 1, 2]).astype(int)
        for h in HORIZONS:
            g[target_col(h)] = g["pm25"].shift(-h)
        tables.append(g.reset_index())
    return pd.concat(tables, ignore_index=True)
