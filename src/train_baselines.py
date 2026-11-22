"""Train baselines, score them on the held-out test period, and save the dashboard inputs.

Run:  python -m src.train_baselines
      optional: --with-forest, and --val-start 2024-04-01 --test-start 2024-10-01 to choose the split

Output files in data/processed/ (the dashboard reads exactly these):
  metrics.csv           station, horizon, model, n_test, rmse, mae, cat_accuracy,
                        pod_very_poor, far_very_poor, events_observed, range_coverage
  test_predictions.csv  station, date, horizon, model, observed, predicted, lower, upper
  latest_forecast.csv   station, issue_date, target_date, horizon, model, predicted, lower, upper, category
"""
import argparse

import pandas as pd

from src.aqi import pm25_category
from src.config import HORIZONS, MIN_TRAIN_ROWS, PROCESSED_DIR
from src.evaluate import (apply_range, category_metrics, chronological_split, coverage,
                          regression_metrics, residual_range, split_dates)
from src.features import FEATURE_COLS, target_col
from src.models import baseline_models


def score_station(station_df, horizon, val_start, test_start, with_forest):
    """Fit all models for one station and horizon. Returns prediction rows and the latest forecast."""
    target = target_col(horizon)
    usable = station_df.dropna(subset=FEATURE_COLS + [target])  # same rows for every model
    train, val, test = chronological_split(usable, horizon, val_start, test_start)
    if len(train) < MIN_TRAIN_ROWS or len(val) < 10 or len(test) < 10:
        return None, None

    # The newest day with complete features is where the "real" forecast starts.
    latest = station_df.dropna(subset=FEATURE_COLS).tail(1)
    pred_rows, latest_rows = [], []
    for model in baseline_models(with_forest):
        model.fit(train, target)
        low_res, high_res = residual_range(val[target], model.predict(val))
        predicted = model.predict(test)
        lower, upper = apply_range(predicted, low_res, high_res)
        pred_rows.append(pd.DataFrame({
            "station": station_df["station"].iloc[0], "date": test["date"].to_numpy(),
            "horizon": horizon, "model": model.name, "observed": test[target].to_numpy(),
            "predicted": predicted, "lower": lower, "upper": upper}))
        if len(latest):
            p = model.predict(latest)
            lo, hi = apply_range(p, low_res, high_res)
            issue = latest["date"].iloc[0]
            latest_rows.append({"station": station_df["station"].iloc[0], "issue_date": issue,
                                "target_date": issue + pd.Timedelta(days=horizon), "horizon": horizon,
                                "model": model.name, "predicted": float(p[0]),
                                "lower": float(lo[0]), "upper": float(hi[0]),
                                "category": pm25_category(pd.Series(p)).iloc[0]})
    return pd.concat(pred_rows), latest_rows


def summarise(predictions):
    """One metrics row per station / horizon / model (all models share the same test days)."""
    rows = []
    for (station, horizon, model), g in predictions.groupby(["station", "horizon", "model"]):
        rows.append({"station": station, "horizon": horizon, "model": model, "n_test": len(g),
                     **regression_metrics(g["observed"], g["predicted"]),
                     **category_metrics(g["observed"], g["predicted"]),
                     "range_coverage": coverage(g["observed"], g["lower"], g["upper"])})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-forest", action="store_true", help="also train the random forest")
    parser.add_argument("--val-start", help="YYYY-MM-DD, first day of the validation block")
    parser.add_argument("--test-start", help="YYYY-MM-DD, first day of the test block (pick one that includes a winter)")
    args = parser.parse_args()

    df = pd.read_csv(PROCESSED_DIR / "daily_features.csv", parse_dates=["date"])
    val_start, test_start = split_dates(df.dropna(subset=["pm25"])["date"])
    if args.val_start and args.test_start:
        val_start, test_start = pd.Timestamp(args.val_start), pd.Timestamp(args.test_start)
    print(f"Validation starts {val_start.date()}, test starts {test_start.date()} (chronological split).")

    all_predictions, all_latest = [], []
    for station, station_df in df.groupby("station"):
        for horizon in HORIZONS:
            preds, latest = score_station(station_df.sort_values("date"), horizon,
                                          val_start, test_start, args.with_forest)
            if preds is None:
                print(f"Skipped {station} (h={horizon}): not enough data in train/val/test.")
                continue
            all_predictions.append(preds)
            all_latest.extend(latest)

    if not all_predictions:
        raise SystemExit("No station had enough data. Check data/processed/missing_report.csv.")
    predictions = pd.concat(all_predictions, ignore_index=True)
    metrics = summarise(predictions)
    predictions.to_csv(PROCESSED_DIR / "test_predictions.csv", index=False)
    metrics.to_csv(PROCESSED_DIR / "metrics.csv", index=False)
    pd.DataFrame(all_latest).to_csv(PROCESSED_DIR / "latest_forecast.csv", index=False)
    print(metrics.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
