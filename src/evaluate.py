"""Chronological split, error metrics, category metrics and forecast ranges (Module 3)."""
import numpy as np
import pandas as pd

from src.aqi import VERY_POOR_INDEX, category_index, pm25_category
from src.config import INTERVAL_HIGH, INTERVAL_LOW, TEST_FRACTION, VAL_FRACTION


def split_dates(dates, val_fraction=VAL_FRACTION, test_fraction=TEST_FRACTION):
    """Return (val_start, test_start): the dates where validation and test blocks begin."""
    unique = np.sort(pd.Series(dates).dropna().unique())
    n = len(unique)
    test_start = unique[int(n * (1 - test_fraction))]
    val_start = unique[int(n * (1 - test_fraction - val_fraction))]
    return pd.Timestamp(val_start), pd.Timestamp(test_start)


def chronological_split(df, horizon, val_start, test_start):
    """Time-ordered train / validation / test. No shuffling.

    A training row dated d has its target on day d + horizon, so it is only used if that
    target day is still before the next block starts. This stops target information
    leaking across the boundary.
    """
    gap = pd.Timedelta(days=horizon)
    train = df[df["date"] + gap < val_start]
    val = df[(df["date"] >= val_start) & (df["date"] + gap < test_start)]
    test = df[df["date"] >= test_start]
    return train, val, test


def regression_metrics(y_true, y_pred):
    err = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)
    return {"rmse": float(np.sqrt(np.mean(err ** 2))), "mae": float(np.mean(np.abs(err)))}


def category_metrics(y_true, y_pred):
    """Category accuracy, plus probability of detection (POD) and false-alarm ratio (FAR)
    for the event 'Very Poor or worse' (PM2.5 sub-index category)."""
    true_idx = pm25_category(pd.Series(np.asarray(y_true))).map(category_index)
    pred_idx = pm25_category(pd.Series(np.asarray(y_pred))).map(category_index)
    accuracy = float((true_idx == pred_idx).mean())
    event_true, event_pred = true_idx >= VERY_POOR_INDEX, pred_idx >= VERY_POOR_INDEX
    hits = int((event_true & event_pred).sum())
    misses = int((event_true & ~event_pred).sum())
    false_alarms = int((~event_true & event_pred).sum())
    pod = hits / (hits + misses) if hits + misses else np.nan
    far = false_alarms / (hits + false_alarms) if hits + false_alarms else np.nan
    return {"cat_accuracy": accuracy, "pod_very_poor": pod, "far_very_poor": far,
            "events_observed": hits + misses}


def residual_range(y_true, y_pred):
    """Low/high residual quantiles (observed - predicted) from held-out validation data."""
    residuals = np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)
    return float(np.quantile(residuals, INTERVAL_LOW)), float(np.quantile(residuals, INTERVAL_HIGH))


def apply_range(pred, low_res, high_res):
    """Prediction +/- residual quantiles; the lower bound cannot go below zero."""
    pred = np.asarray(pred, dtype=float)
    return np.clip(pred + low_res, 0, None), np.clip(pred + high_res, 0, None)


def coverage(y_true, lower, upper):
    """Share of observed values that fall inside the forecast range."""
    y_true = np.asarray(y_true, dtype=float)
    return float(np.mean((y_true >= lower) & (y_true <= upper)))
