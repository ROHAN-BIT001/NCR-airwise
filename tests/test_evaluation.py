"""T4 no leakage, and metric sanity checks."""
import numpy as np
import pandas as pd

from src.evaluate import (apply_range, category_metrics, chronological_split, coverage,
                          regression_metrics, split_dates)


def _frame(days=400):
    return pd.DataFrame({"date": pd.date_range("2024-01-01", periods=days, freq="D")})


def test_test_period_is_strictly_after_training():  # T4
    df = _frame()
    val_start, test_start = split_dates(df["date"])
    for horizon in (1, 2):
        train, val, test = chronological_split(df, horizon, val_start, test_start)
        assert train["date"].max() < val["date"].min() < test["date"].min()
        # a training target (date + horizon) never reaches into validation or test days
        assert train["date"].max() + pd.Timedelta(days=horizon) < val_start
        assert val["date"].max() + pd.Timedelta(days=horizon) < test_start


def test_split_blocks_do_not_overlap_and_cover_recent_data():
    df = _frame()
    val_start, test_start = split_dates(df["date"])
    train, val, test = chronological_split(df, 1, val_start, test_start)
    assert len(set(train["date"]) & set(test["date"])) == 0
    assert test["date"].max() == df["date"].max()


def test_regression_metrics():
    m = regression_metrics([10, 20], [12, 16])
    assert m["mae"] == 3.0 and abs(m["rmse"] - np.sqrt(10)) < 1e-9


def test_category_metrics_pod_and_far():
    observed = [10, 150, 150, 10]   # two Very Poor days (PM2.5 > 120)
    predicted = [10, 150, 20, 150]  # one hit, one miss, one false alarm
    m = category_metrics(observed, predicted)
    assert m["pod_very_poor"] == 0.5
    assert m["far_very_poor"] == 0.5
    assert m["events_observed"] == 2


def test_range_never_below_zero_and_coverage():
    lower, upper = apply_range([5.0, 50.0], -20.0, 10.0)
    assert lower[0] == 0.0 and upper[1] == 60.0
    assert coverage([5.0, 100.0], lower, upper) == 0.5
