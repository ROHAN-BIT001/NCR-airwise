# Data sources and licence check (Udbhav)

Fill in from your own checking. Do not guess licence terms; copy them from the source pages.

## Air quality (CPCB)
- Where downloaded from (URL, portal name):
- Date downloaded:
- Stations downloaded:
- Terms of use / licence (quote the page and link it):
- Expected file format: one CSV per station in `data/raw/cpcb/`, with a date/time column
  (e.g. `From Date`, dd-mm-yyyy HH:MM, IST) and `PM2.5`, `PM10` columns. If the station is not a
  column, the file name is used as the station name. Other column names: add them to
  `COLUMN_ALIASES` in `src/config.py`.

## Weather (Open-Meteo historical API)
- Endpoint used: `https://archive-api.open-meteo.com/v1/archive`
- Terms of use / licence (link the page and note any attribution required):
- Date range downloaded:
- Variables: temperature, relative humidity, wind speed (m/s), wind direction, precipitation

## Station choice
- Stations considered and their missing-data share (from `data/processed/missing_report.csv`):
- Final stations and why:

## Dataset documentation
- Columns in `daily_features.csv` and their units:
- Known problems found in the raw data:
