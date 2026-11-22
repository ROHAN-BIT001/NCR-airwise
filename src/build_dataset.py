"""Raw files -> cleaned daily feature table (Module 1 + 2).

Run:  python -m src.build_dataset
"""
from src.cleaning import (fill_short_gaps, flag_outliers, merge_hourly, missing_report,
                          prepare_weather, remove_impossible, to_daily, to_hourly)
from src.config import PROCESSED_DIR
from src.data_loading import load_air, load_weather
from src.features import add_features


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    air = load_air()
    air, removed = remove_impossible(air)
    print(f"Removed {removed} impossible pollutant values (set to missing).")
    air = flag_outliers(air)
    print(f"Flagged {int(air['pm25_outlier'].sum())} extreme PM2.5 readings (kept in the data).")

    hourly = to_hourly(air)
    report = missing_report(hourly)  # measured before any gap filling
    report.to_csv(PROCESSED_DIR / "missing_report.csv", index=False)
    print(report.to_string(index=False))

    hourly = fill_short_gaps(hourly)
    merged = merge_hourly(hourly, prepare_weather(load_weather()))
    if merged["temp"].isna().all():
        print("WARNING: no weather matched. Check that station names agree in both folders.")

    daily = add_features(to_daily(merged))
    daily.to_csv(PROCESSED_DIR / "daily_features.csv", index=False)
    print(f"Saved {len(daily)} station-days to data/processed/daily_features.csv")


if __name__ == "__main__":
    main()
