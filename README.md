# NCR AIRWISE

Air-Pollution–Weather Coupled Forecasting & Awareness Dashboard for Delhi-NCR
(Problem Bank SIH26082), 2026CSAE102 Technology and Sustainability, Bennett University.

A student prototype that shows observed air quality and weather together, adds a 1–2 day PM2.5
forecast with a stated range, and keeps observed data visibly separate from the team's own
predictions. It is **not** an official forecast and gives no health advice.

The data ends in mid-2020, so the dashboard shows the latest available day, not live data.

## Team

| Member | Enrollment | Role and work in this repository |
| --- | --- | --- |
| Rohan Jha | S26CSEU2457 | Coordinator. Data pipeline, AQI and features, dashboard (all panels and shell), tests, test log, README, synopsis and contribution log. |
| Udbhav Saxena | S26CSEU2582 | Data and technology lead. Data sources and licences, baseline models, evaluation, training script and results. |
| Manan Jain | S26CSEU2543 | Sustainability and documentation lead. Milestone 1 sustainability and SDG mapping, requirements and documentation. |

The real record of who did what is `docs/contribution_log.md` and the Git history
(`git shortlog -sn`).

## Setup

Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

## Data

Raw and processed data files are not stored in Git. The shared Drive folder holds them:
https://drive.google.com/drive/folders/1oCO2fEoyGxr4SgOur7SwkDjJ-pKXcrQ1?usp=sharing

To skip the download and processing steps, copy `daily_features.csv`, `missing_report.csv`,
`metrics.csv`, `latest_forecast.csv` and `test_predictions.csv` from that folder into
`data/processed/` and go straight to step 5 below.

## How to run (always from the project root)

```bash
# 1. Download stations.csv and station_hour.csv from the Kaggle dataset
#    "Air Quality Data in India (2015 - 2020)" into data/raw/kaggle/   (see docs/data_sources.md)
python -m src.prepare_kaggle
# 2. Download weather for the same stations and dates (needs internet)
python -m src.fetch_weather --start 2015-01-01 --end 2020-07-01
# 3. Clean, merge, compute AQI and features
python -m src.build_dataset
# 4. Train baselines and evaluate on the held-out period
python -m src.train_baselines
# 5. Open the dashboard
python -m streamlit run app/streamlit_app.py
# 6. Run the tests
python -m pytest
```

The default split puts the test block from 2019-07-23 to 2020-07-01, so it includes winter
2019-20. The random forest is planned for Milestone 3 and is not run by default.

## Results and tests

- Baseline results (persistence, climatology, ridge regression) and how to read them:
  `docs/data_sources.md` and `data/processed/metrics.csv`.
- Test results T1 to T7 with the run date and screenshots: `docs/test_log.md` and `docs/evidence/`.
- Technical synopsis (Milestone 2 document): `docs/synopsis.md`.

## Project layout

```
src/config.py            all settings (stations, paths, thresholds)
src/prepare_kaggle.py    split the Kaggle CPCB file into one CSV per station
src/data_loading.py      read raw CPCB and weather files
src/fetch_weather.py     download weather from Open-Meteo
src/cleaning.py          IST timestamps, bad values, gaps, merge, daily means
src/aqi.py               CPCB AQI sub-index and category
src/features.py          lags, rolling means, weather and calendar features, targets
src/build_dataset.py     runs the whole data pipeline
src/models.py            persistence, climatology, ridge (random forest planned for Milestone 3)
src/evaluate.py          chronological split, RMSE/MAE, category metrics, forecast range
src/train_baselines.py   trains, scores, writes the files the dashboard reads
app/streamlit_app.py     dashboard shell (station and date selectors, panel order)
app/common.py            shared helpers, colours and data loading
app/text.py              all wording shown in the dashboard
app/panels/              one file per panel: status, trends, relationships, forecast, about
tests/                   automated tests (see docs/test_log.md)
docs/                    data sources, test log, evidence, synopsis, contribution log
```

## Files passed between modules (the "contract")

| File (data/processed/) | Written by | Read by |
| --- | --- | --- |
| `daily_features.csv` | `build_dataset` | `train_baselines`, panels 1 to 3 |
| `missing_report.csv` | `build_dataset` | dataset documentation |
| `metrics.csv`, `test_predictions.csv`, `latest_forecast.csv` | `train_baselines` | forecast panel and About page |

Column lists are in the docstring of `src/train_baselines.py` and in `docs/data_sources.md`.

## Data sources and acknowledgements

Full details, licences and station statistics are in `docs/data_sources.md`.

- **Air quality:** Kaggle dataset "Air Quality Data in India (2015 - 2020)" by Rohan Rao,
  https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india. The data was made public by
  the Central Pollution Control Board (CPCB), Government of India. Licence on the Kaggle page:
  CC0: Public Domain.
- **Weather:** Open-Meteo historical weather API, https://open-meteo.com/ (CC BY 4.0, non-commercial
  use). Weather data by Open-Meteo.com.
- **AQI categories:** CPCB National Air Quality Index bands, implemented in `src/aqi.py`.
- **Background evidence (Milestone 1):** Ignatious, S. M. and Rafiuddin, M. (2025), *How Well Can Delhi
  Predict Air Quality?*, Council on Energy, Environment and Water (CEEW) issue brief; IMD air-quality
  forecasting SOP; the 2024 Lancet Planetary Health multi-city PM2.5 mortality study. Full list in the
  Milestone 1 report.
- **Tools:** Python, pandas, NumPy, scikit-learn, Plotly, Streamlit, pytest.

## Limitations

- The data ends in mid-2020, so the dashboard shows the latest available day, not live data.
- Hourly values are missing at every station, most at ITO (about 55% of PM2.5). Dwarka Sector 8
  starts only in February 2018.
- AQI is calculated from PM2.5 and PM10 only, so it can differ from official AQI reports.
- Weather is modelled data, not station measurements, and observed (not forecast) weather is used as
  model input.
- Forecast ranges are wide: they are 90% ranges from validation errors that include a winter.
- Correlation between weather and pollution is not proof of cause.
- Student prototype. Not an official forecast. No medical advice. The wording shown in the
  dashboard is in `app/text.py`.
