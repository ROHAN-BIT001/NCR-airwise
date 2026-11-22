"""Cleaning, timestamp alignment, merging and daily aggregation (Module 1 and 2)."""
import numpy as np
import pandas as pd

from src.aqi import category_from_aqi, compute_aqi
from src.config import (MAX_INTERPOLATE_HOURS, MAX_VALID, MIN_HOURS_PER_DAY,
                        OUTLIER_MAD_FACTOR)

POLLUTANTS = ["pm25", "pm10"]
WEATHER = ["temp", "rh", "wind_speed", "wind_sin", "wind_cos"]


def to_ist(series):
    """Return naive timestamps expressed in IST. Naive input is assumed to already be IST."""
    series = pd.to_datetime(series, errors="coerce")
    if series.dt.tz is not None:
        series = series.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    return series


def remove_impossible(df):
    """Negative or implausibly large concentrations become NaN. Returns the table and a count."""
    df = df.copy()
    removed = 0
    for col in POLLUTANTS:
        bad = (df[col] < 0) | (df[col] > MAX_VALID[col])
        removed += int(bad.sum())
        df.loc[bad, col] = np.nan
    return df, removed


def flag_outliers(df):
    """Add pm25_outlier: True for extreme spikes per station. Values are kept, only flagged."""
    df = df.copy()
    flags = pd.Series(False, index=df.index)
    for _, group in df.groupby("station"):
        median = group["pm25"].median()
        mad = (group["pm25"] - median).abs().median() * 1.4826
        if mad > 0:
            flags.loc[group.index] = group["pm25"] > median + OUTLIER_MAD_FACTOR * mad
    df["pm25_outlier"] = flags
    return df


def to_hourly(air):
    """One row per station and hour (duplicate timestamps averaged); gaps appear as NaN rows."""
    air = air.dropna(subset=["datetime"]).copy()
    air["datetime"] = to_ist(air["datetime"])
    hourly = (air.set_index("datetime").groupby("station")[POLLUTANTS]
              .resample("h").mean().reset_index())
    return hourly


def missing_report(hourly):
    """Share of hours with no PM2.5 / PM10, per station (call before filling gaps)."""
    rows = []
    for station, group in hourly.groupby("station"):
        rows.append({"station": station, "hours": len(group),
                     "start": group["datetime"].min(), "end": group["datetime"].max(),
                     "pm25_missing_share": group["pm25"].isna().mean(),
                     "pm10_missing_share": group["pm10"].isna().mean()})
    return pd.DataFrame(rows)


def fill_short_gaps(hourly):
    """Interpolate gaps of up to MAX_INTERPOLATE_HOURS; longer gaps stay missing."""
    hourly = hourly.sort_values(["station", "datetime"]).copy()
    for col in POLLUTANTS:
        hourly[col] = hourly.groupby("station")[col].transform(
            lambda s: s.interpolate(limit=MAX_INTERPOLATE_HOURS, limit_area="inside"))
    return hourly


def prepare_weather(weather):
    """Wind direction -> sine/cosine so that 359 and 1 degrees are neighbours."""
    weather = weather.copy()
    weather["datetime"] = to_ist(weather["datetime"])
    radians = np.deg2rad(weather["wind_dir"])
    weather["wind_sin"], weather["wind_cos"] = np.sin(radians), np.cos(radians)
    return weather.drop_duplicates(["station", "datetime"])


def merge_hourly(air_hourly, weather):
    """Join pollutants and weather on station and IST hour (keeps all air rows)."""
    merged = air_hourly.merge(weather.drop(columns=["wind_dir"]), on=["station", "datetime"], how="left")
    assert not merged.duplicated(["station", "datetime"]).any(), "duplicate station-hour rows"
    return merged


def to_daily(hourly):
    """Daily means (rain = daily total). A pollutant mean needs MIN_HOURS_PER_DAY valid hours."""
    hourly = hourly.copy()
    hourly["date"] = hourly["datetime"].dt.normalize()
    grouped = hourly.groupby(["station", "date"])
    daily = grouped[POLLUTANTS + WEATHER].mean()
    daily["rain"] = grouped["rain"].sum(min_count=1)
    for col in POLLUTANTS:
        valid_hours = grouped[col].count()
        daily.loc[valid_hours < MIN_HOURS_PER_DAY, col] = np.nan
        daily[f"{col}_hours"] = valid_hours
    daily = daily.reset_index()
    daily["aqi"] = compute_aqi(daily["pm25"], daily["pm10"])
    daily["aqi_category"] = daily["aqi"].apply(category_from_aqi)
    return daily
