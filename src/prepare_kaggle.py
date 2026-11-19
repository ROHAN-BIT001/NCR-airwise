"""Split the Kaggle 'Air Quality Data in India (2015-2020)' files into one CSV per project station.

Run (after putting stations.csv and station_hour.csv in data/raw/kaggle/):
    python -m src.prepare_kaggle

Output: data/raw/cpcb/<station>.csv with columns Station, Datetime (dd-mm-yyyy HH:MM, IST), PM2.5, PM10.
The Station column uses the names from STATIONS in src/config.py, so weather files match automatically.
"""
import pandas as pd

from src.config import RAW_AIR_DIR, ROOT, STATIONS

KAGGLE_DIR = ROOT / "data" / "raw" / "kaggle"


def squash(name):
    """Lower-case letters and digits only, so 'R K Puram' and 'RK Puram' compare equal."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def find_station_ids(stations):
    """Map each configured station name to the Kaggle StationId whose name starts with it."""
    delhi = stations[stations["City"].str.lower() == "delhi"]
    found = {}
    for wanted in STATIONS:
        matches = delhi[delhi["StationName"].map(squash).str.startswith(squash(wanted))]
        if len(matches) == 1:
            found[wanted] = matches["StationId"].iloc[0]
            print(f"{wanted}: {found[wanted]} ({matches['StationName'].iloc[0]})")
        elif len(matches) == 0:
            print(f"WARNING: no Delhi station in stations.csv starts with '{wanted}'. Skipped.")
        else:
            print(f"WARNING: '{wanted}' matches several stations: {list(matches['StationName'])}. Skipped.")
    return found


def main():
    stations = pd.read_csv(KAGGLE_DIR / "stations.csv")
    ids = find_station_ids(stations)
    if not ids:
        raise SystemExit("No stations matched. Check the names in stations.csv against STATIONS in src/config.py.")

    RAW_AIR_DIR.mkdir(parents=True, exist_ok=True)
    wanted_ids = set(ids.values())
    chunks = pd.read_csv(KAGGLE_DIR / "station_hour.csv", usecols=["StationId", "Datetime", "PM2.5", "PM10"],
                         chunksize=500_000)  # the file is large, so read it in pieces
    kept = pd.concat([c[c["StationId"].isin(wanted_ids)] for c in chunks], ignore_index=True)
    kept["Datetime"] = pd.to_datetime(kept["Datetime"], errors="coerce")  # Kaggle uses yyyy-mm-dd HH:MM:SS (IST)

    for name, station_id in ids.items():
        one = kept[kept["StationId"] == station_id].copy()
        one.insert(0, "Station", name)
        one["Datetime"] = one["Datetime"].dt.strftime("%d-%m-%Y %H:%M")  # the format our loader expects
        out = RAW_AIR_DIR / f"{name.lower().replace(' ', '_')}.csv"
        one[["Station", "Datetime", "PM2.5", "PM10"]].to_csv(out, index=False)
        print(f"Saved {len(one)} hourly rows for {name} -> {out}")


if __name__ == "__main__":
    main()
