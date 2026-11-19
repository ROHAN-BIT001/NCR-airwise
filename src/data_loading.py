"""Read raw CPCB air-quality files and Open-Meteo weather files (Module 1)."""
import re

import pandas as pd

from src.config import COLUMN_ALIASES, DAYFIRST, RAW_AIR_DIR, RAW_WEATHER_DIR


def clean_station_name(name):
    """'Anand Vihar, Delhi - DPCC' -> 'anand vihar delhi dpcc'. Used so names match across files."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(name).lower()).split())


def load_air(folder=RAW_AIR_DIR):
    """Load every CSV in the folder into one table: station, datetime, pm25, pm10."""
    files = sorted(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CPCB CSV files found in {folder}. See docs/data_sources.md.")
    tables = []
    for path in files:
        df = pd.read_csv(path)
        df.columns = [COLUMN_ALIASES.get(c.strip().lower(), c.strip().lower()) for c in df.columns]
        if "station" not in df.columns:
            df["station"] = path.stem  # one file per station: use the file name
        if "datetime" not in df.columns or "pm25" not in df.columns:
            raise ValueError(f"{path.name} needs a date/time column and a PM2.5 column.")
        if "pm10" not in df.columns:
            df["pm10"] = float("nan")
        df["datetime"] = pd.to_datetime(df["datetime"], dayfirst=DAYFIRST, errors="coerce")
        for col in ("pm25", "pm10"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["station"] = df["station"].map(clean_station_name)
        tables.append(df[["station", "datetime", "pm25", "pm10"]])
    return pd.concat(tables, ignore_index=True)


def load_weather(folder=RAW_WEATHER_DIR):
    """Load weather CSVs written by src/fetch_weather.py (hourly, already in IST)."""
    files = sorted(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No weather CSV files found in {folder}. Run: python -m src.fetch_weather")
    df = pd.concat([pd.read_csv(p) for p in files], ignore_index=True)
    df = df.rename(columns={"time": "datetime", "temperature_2m": "temp", "relative_humidity_2m": "rh",
                            "wind_speed_10m": "wind_speed", "wind_direction_10m": "wind_dir",
                            "precipitation": "rain"})
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["station"] = df["station"].map(clean_station_name)
    return df[["station", "datetime", "temp", "rh", "wind_speed", "wind_dir", "rain"]]
