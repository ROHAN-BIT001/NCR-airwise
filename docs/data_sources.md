# Data sources and licence check (Udbhav)

Licence wording below was last verified against the linked pages on 22 November 2026.

## Air quality (CPCB, via Kaggle)
- Where downloaded from: Kaggle dataset "Air Quality Data in India (2015 - 2020)" by Rohan Rao,
  https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india
- Original source: the data was made publicly available by the Central Pollution Control Board (CPCB), the official portal of the Government of India (https://cpcb.nic.in/).
- Files used: `stations.csv` (station list) and `station_hour.csv` (hourly readings). Only the two pollutants we need (PM2.5 and PM10) are kept. `src/prepare_kaggle.py` matches our five stations to their Kaggle station IDs and splits the large file into one CSV per station.
- Coverage: hourly data, 2015 to mid-2020 (the last hour used is 2020-07-01).
- Time zone: Kaggle timestamps are local time (IST). The pipeline treats timestamps without a time-zone label as IST.
- Terms of use / licence: the Kaggle page lists the licence as **CC0: Public Domain**. Attribution is not legally required under CC0, but the dataset author and CPCB are credited here and in the dashboard.
- File format used by the pipeline: one CSV per station in `data/raw/cpcb/` with `Station`, `Datetime` (dd-mm-yyyy HH:MM), `PM2.5` and `PM10` columns.

## Weather (Open-Meteo historical API)
- Endpoint used: `https://archive-api.open-meteo.com/v1/archive`
- Terms of use / licence: Open-Meteo data is offered under **Attribution 4.0 International (CC BY 4.0)**. The free API is for non-commercial use (fair use, up to 10,000 calls a day). This student project is non-commercial and makes only a few calls, one per station. Terms page: https://open-meteo.com/en/terms
- Attribution required: "Weather data by Open-Meteo.com" with a link to https://open-meteo.com/. This credit is given here and in the dashboard's data-source list.
- Date range downloaded: 2015-01-01 to 2020-07-01.
- Variables: temperature (°C), relative humidity (%), wind speed (m/s), wind direction (degrees), precipitation (mm).
- Location: one request per station, using the station's approximate coordinates from `src/config.py`.
- Note: the historical archive is modelled reanalysis data on a grid, not a measurement at the station.

## Station choice
- Stations considered and their missing-data share (from `data/processed/missing_report.csv`):

| Station | Hours | Starts | PM2.5 missing | PM10 missing |
| --- | --- | --- | --- | --- |
| Anand Vihar | 45,950 | Apr 2015 | 21.1% | 25.8% |
| Dwarka Sector 8 | 21,137 | Feb 2018 | 1.3% | 3.6% |
| ITO | 48,128 | Jan 2015 | 55.3% | 46.0% |
| Punjabi Bagh | 45,872 | Apr 2015 | 25.4% | 25.6% |
| RK Puram | 45,950 | Apr 2015 | 20.1% | 16.1% |

- Final stations and why: all five are kept. They are well-known Delhi monitoring stations spread across the city, and all five have usable PM2.5 and PM10 data. ITO is the weakest (more than half of its PM2.5 hours are missing, so only about 790 days are usable, from late 2017), and Dwarka Sector 8 has a short history (it starts in February 2018). Results for these two should be read with care. No station was removed, because none is unusable.

## Cleaning rules (src/cleaning.py, settings in src/config.py)
- PM2.5 above 1500 µg/m³ and PM10 above 2500 µg/m³ are treated as impossible and set to missing.
- Values far above the station's typical level (more than 10 robust standard deviations above the median) are flagged as outliers but not deleted.
- Gaps of up to 3 hours are filled by interpolation. Longer gaps stay missing.
- A daily mean needs at least 18 valid hours, otherwise the day is left blank.
- Weather and pollution are joined on station and IST hour.

## Dataset documentation
- Columns in `daily_features.csv` and their units:
  - `date`, `station`
  - `pm25`, `pm10`: daily mean in µg/m³; blank if fewer than 18 valid hours that day
  - `temp` (°C), `rh` (%), `wind_speed` (m/s), `wind_sin` and `wind_cos` (no unit, wind direction as sine and cosine), `rain` (mm, daily total)
  - `pm25_hours`, `pm10_hours`: number of valid hours behind each daily mean
  - `aqi`, `aqi_category`: calculated from PM2.5 and PM10 only, using CPCB bands
  - `pm25_lag1`, `pm25_lag2`, `pm25_lag3`: PM2.5 from 1, 2 and 3 days earlier
  - `pm25_roll3`, `pm25_roll7`: rolling means of past days
  - `month`, `month_sin`, `month_cos`, `dayofweek` (0 = Monday), `season_flag` (1 for October to February)
  - `target_pm25_h1`, `target_pm25_h2`: PM2.5 one and two days ahead (the values being predicted)
- Known problems found in the raw data:
  - Hourly values are missing at every station, most at ITO (55.3% of PM2.5).
  - Dwarka Sector 8 starts only in 2018, so its training period has no full winter.
  - Impossible values are set to missing, outliers are flagged and kept, and short gaps are filled (see the cleaning rules above).
  - AQI here uses only PM2.5 and PM10, so it can differ from official AQI reports.

## Limitations
- The data ends in mid-2020, so the dashboard shows the latest available day, not live data. The latest forecast is for 1 and 2 July 2020 and is not a real forecast for today.
- Hourly values can be missing, and a day needs at least 18 valid hours to get a daily mean.
- Weather is modelled data, not station measurements.
- This is a student prototype. It is not an official forecast and gives no health advice.

## Results of the baseline run
- Run date: 22 November 2026, with `python -m src.train_baselines` on the real `daily_features.csv`.
- Chronological split: the oldest dates are used for training, then 15% of dates for validation (used for the forecast ranges), then the newest 20% for testing. Validation starts 2018-11-07 and the test block starts 2019-07-23, so the test period includes winter 2019-20 and runs to 2020-07-01.
- Forecast range: the 5th to 95th percentile of validation errors, so a 90% range.
- Models compared: persistence (tomorrow equals today), climatology (month average) and ridge regression. The random forest is planned for Milestone 3 and was not run.
- Averages over the five stations (RMSE and MAE in µg/m³; POD and FAR for Very Poor and worse days):

| Horizon | Model | RMSE | MAE | POD | FAR |
| --- | --- | --- | --- | --- | --- |
| 1 day | persistence | 50.7 | 30.0 | 0.83 | 0.17 |
| 1 day | ridge | 48.4 | 30.3 | 0.95 | 0.24 |
| 1 day | climatology | 84.7 | 62.0 | 0.85 | 0.43 |
| 2 days | persistence | 67.8 | 42.0 | 0.76 | 0.24 |
| 2 days | ridge | 60.8 | 41.0 | 0.95 | 0.30 |
| 2 days | climatology | 85.0 | 62.3 | 0.85 | 0.42 |

- RMSE by station (persistence vs ridge, 1 and 2 days ahead, µg/m³):

| Station | 1 day persistence | 1 day ridge | 2 days persistence | 2 days ridge | Test days (1 day) |
| --- | --- | --- | --- | --- | --- |
| Anand Vihar | 58.5 | 55.8 | 77.1 | 68.8 | 200 |
| Dwarka Sector 8 | 50.3 | 50.9 | 67.8 | 62.6 | 333 |
| ITO | 49.1 | 46.0 | 66.4 | 57.8 | 265 |
| Punjabi Bagh | 53.4 | 49.7 | 72.4 | 64.6 | 289 |
| RK Puram | 42.0 | 39.5 | 55.1 | 50.2 | 294 |

- What the results show: ridge has the lowest average RMSE at both horizons. At 1 day the improvement over persistence is small (48.4 against 50.7) and the MAE is about equal. At 2 days the improvement is clearer (60.8 against 67.8). Persistence is slightly better at Dwarka Sector 8 for 1 day. Ridge catches more Very Poor and worse days (POD about 0.95 against 0.83 at 1 day) but gives more false alarms (FAR 0.24 against 0.17). Climatology is clearly the worst because it uses only the month. These models are simple baselines and are not expected to beat official forecasting systems.
- Output files: `data/processed/metrics.csv` (committed), `latest_forecast.csv` and `test_predictions.csv` (shared on Drive, not committed).

## Credits
- Air quality data: Central Pollution Control Board (CPCB), Government of India, as compiled on Kaggle by Rohan Rao (CC0).
- Weather data: Open-Meteo.com (CC BY 4.0), https://open-meteo.com/
- AQI categories: CPCB National Air Quality Index bands, implemented in `src/aqi.py`.

## How to reproduce the data
1. Download the Kaggle files `stations.csv` and `station_hour.csv` into `data/raw/kaggle/`.
2. `python -m src.prepare_kaggle`
3. `python -m src.fetch_weather --start 2015-01-01 --end 2020-07-01`
4. `python -m src.build_dataset`
5. `python -m src.train_baselines`
