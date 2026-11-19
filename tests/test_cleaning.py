"""T1 timestamp alignment, T3 missing data, plus cleaning rules."""
import numpy as np
import pandas as pd

from src.cleaning import (fill_short_gaps, merge_hourly, missing_report, prepare_weather,
                          remove_impossible, to_daily, to_hourly, to_ist)


def _air(hours=48, station="a"):
    times = pd.date_range("2025-01-01", periods=hours, freq="h")
    return pd.DataFrame({"station": station, "datetime": times, "pm25": 100.0, "pm10": 150.0})


def test_to_ist_converts_utc_and_keeps_naive():
    utc = pd.Series(pd.to_datetime(["2025-01-01 00:00"]).tz_localize("UTC"))
    assert to_ist(utc).iloc[0] == pd.Timestamp("2025-01-01 05:30")
    naive = pd.Series(pd.to_datetime(["2025-01-01 10:00"]))
    assert to_ist(naive).iloc[0] == pd.Timestamp("2025-01-01 10:00")


def test_negative_and_huge_values_removed():
    df = _air(3)
    df.loc[0, "pm25"] = -4
    df.loc[1, "pm25"] = 99999
    cleaned, removed = remove_impossible(df)
    assert removed == 2 and cleaned["pm25"].isna().sum() == 2


def test_merge_has_no_duplicate_or_shifted_hours():  # T1
    air = to_hourly(pd.concat([_air(), _air().iloc[:1]]))  # one duplicated timestamp
    weather = pd.DataFrame({"station": "a", "datetime": air["datetime"], "temp": 10.0, "rh": 50.0,
                            "wind_speed": 2.0, "wind_dir": 90.0, "rain": 0.0})
    merged = merge_hourly(air, prepare_weather(weather))
    assert not merged.duplicated(["station", "datetime"]).any()
    assert len(merged) == len(air) == 48
    assert merged["temp"].notna().all()


def test_missing_share_reported_per_station():  # T3
    a, b = _air(10, "a"), _air(10, "b")
    b.loc[:4, "pm25"] = np.nan
    report = missing_report(to_hourly(pd.concat([a, b]))).set_index("station")
    assert report.loc["a", "pm25_missing_share"] == 0
    assert report.loc["b", "pm25_missing_share"] == 0.5


def test_only_short_gaps_are_filled():
    df = _air(20)
    df.loc[2:3, "pm25"] = np.nan  # 2-hour gap: filled
    df.loc[8:13, "pm25"] = np.nan  # 6-hour gap: only partly filled (limit 3), rest stays missing
    filled = fill_short_gaps(to_hourly(df))
    assert filled["pm25"].iloc[2:4].notna().all()
    assert filled["pm25"].iloc[8:14].isna().any()


def test_daily_mean_needs_enough_hours():
    df = _air(48)
    df.loc[24:40, "pm25"] = np.nan  # day 2 keeps only 7 valid hours
    hourly = to_hourly(df)
    hourly["rain"] = 0.0
    for col in ["temp", "rh", "wind_speed", "wind_sin", "wind_cos"]:
        hourly[col] = 1.0
    daily = to_daily(hourly)
    assert daily["pm25"].iloc[0] == 100.0 and np.isnan(daily["pm25"].iloc[1])
