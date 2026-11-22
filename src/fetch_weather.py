"""Download hourly historical weather for each station from Open-Meteo (Module 1).

Run:  python -m src.fetch_weather --start 2021-01-01 --end 2025-12-31
Needs internet. Open-Meteo's terms and licence are noted in docs/data_sources.md.
"""
import argparse

import pandas as pd
import requests

from src.config import RAW_WEATHER_DIR, STATIONS
from src.data_loading import clean_station_name

URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY = "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation"


def fetch_station(name, lat, lon, start, end):
    params = {"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
              "hourly": HOURLY, "timezone": "Asia/Kolkata", "wind_speed_unit": "ms"}
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()
    df = pd.DataFrame(response.json()["hourly"])
    df.insert(0, "station", clean_station_name(name))
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    RAW_WEATHER_DIR.mkdir(parents=True, exist_ok=True)
    for name, (lat, lon) in STATIONS.items():
        df = fetch_station(name, lat, lon, args.start, args.end)
        out = RAW_WEATHER_DIR / f"{clean_station_name(name).replace(' ', '_')}.csv"
        df.to_csv(out, index=False)
        print(f"Saved {len(df)} hourly rows for {name} -> {out}")


if __name__ == "__main__":
    main()
