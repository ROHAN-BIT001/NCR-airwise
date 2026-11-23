# Technical Synopsis (Milestone 2 document)

**Title:** NCR AIRWISE: Air-Pollution–Weather Coupled Forecasting & Awareness Dashboard for Delhi-NCR

**Team:** Rohan Jha (S26CSEU2457), Udbhav Saxena (S26CSEU2582), Manan Jain (S26CSEU2543)
**Course:** 2026CSAE102 Technology and Sustainability, Bennett University. Problem Bank reference SIH26082.
**Repository:** https://github.com/ROHAN-BIT001/NCR-airwise

## Problem
Delhi-NCR faces recurring severe air pollution driven by emissions and by weather conditions such as wind, humidity and temperature. Official forecasting systems exist, but published evaluations report limited data accessibility and under-prediction in some seasons. Citizens have few simple tools that show observed air quality and weather context together.

## Objective
To build a transparent student prototype that combines public air-quality and weather data, explains how they relate, and produces a 1–2 day PM2.5 forecast with stated uncertainty, clearly separated from official data. It does not replace official monitoring or forecasting and gives no health advice.

## Method
1. **Data.** Hourly PM2.5 and PM10 for five Delhi stations (Anand Vihar, Dwarka Sector 8, ITO, Punjabi Bagh, RK Puram) from the CPCB data on Kaggle ("Air Quality Data in India 2015–2020", CC0), and hourly weather from the Open-Meteo historical API (CC BY 4.0), for 2015-01-01 to 2020-07-01.
2. **Cleaning.** Timestamps are aligned to IST, impossible values are set to missing, outliers are flagged, gaps of up to 3 hours are filled, and a daily mean needs at least 18 valid hours. Daily AQI is calculated from PM2.5 and PM10 with the CPCB bands.
3. **Features.** Lags of 1, 2 and 3 days, rolling 3-day and 7-day means, weather variables, wind direction as sine and cosine, and calendar features. Targets are PM2.5 one and two days ahead.
4. **Models.** Three baselines: persistence (tomorrow equals today), climatology (month average) and ridge regression. A tree-based model (random forest) is planned for Milestone 3.
5. **Evaluation.** A chronological split (oldest 65% for training, 15% for validation, newest 20% for testing). Validation starts 2018-11-07 and the test block starts 2019-07-23, so the test period includes winter 2019-20. Metrics are RMSE, MAE and category-based POD and FAR for Very Poor and worse days. Forecast ranges are the 5th to 95th percentile of validation errors.
6. **Dashboard.** A Streamlit app with a station and date selector and five panels: current status, trends over AQI bands, pollution-weather relationships, forecast (observed in blue, the team's model in red) and an About page with data sources and limitations.

## Progress at Milestone 2
- Data pipeline, AQI functions, features, baselines, evaluation and the full dashboard are built, merged on `main` and run on the real data.
- 19 automated tests pass (timestamp alignment, AQI boundaries, missing-data reporting, no leakage between training and test periods, feature lags and metrics). Manual dashboard tests T6 and T7 were run on three stations with screenshots. Evidence is in `docs/test_log.md` and `docs/evidence/`.

## Results of the baseline run
Averages over the five stations on the held-out test period (RMSE and MAE in µg/m³):

| Horizon | Model | RMSE | MAE |
| --- | --- | --- | --- |
| 1 day | persistence | 50.7 | 30.0 |
| 1 day | ridge | 48.4 | 30.3 |
| 1 day | climatology | 84.7 | 62.0 |
| 2 days | persistence | 67.8 | 42.0 |
| 2 days | ridge | 60.8 | 41.0 |
| 2 days | climatology | 85.0 | 62.3 |

Ridge regression has the lowest RMSE at both horizons. At 1 day its improvement over persistence is small and the MAE is about equal. At 2 days the improvement is clearer. Ridge also catches more Very Poor and worse days (POD about 0.95 against 0.83 for persistence at 1 day) but raises more false alarms (FAR 0.24 against 0.17). Climatology is clearly the weakest. Per-station results are in `docs/data_sources.md` and `data/processed/metrics.csv`. These simple baselines are not expected to beat official forecasting systems, and the results are not directly comparable with published evaluations because the period, stations and data differ.

## Limitations
- The data ends in mid-2020, so the dashboard shows the latest available day, not live data.
- Hourly values are missing at every station, most at ITO (about 55% of PM2.5). Dwarka Sector 8 starts only in February 2018, so its training period has no full winter.
- AQI uses only PM2.5 and PM10, so it can differ from official AQI reports. Weather is modelled data, not station measurements.
- Forecast ranges are wide (the lower bound is often 0). Correlation between weather and pollution is not proof of cause.

## Next steps (Milestone 3)
A random forest comparison on the same split, updated results, and the final report, presentation and demonstration. A bias-correction experiment will be added only if time allows.

## Sustainability relevance
Supports SDG 3 (health, target 3.9), SDG 11 (cities, target 11.6) and SDG 13 (climate awareness, target 13.3).

**Keywords:** air quality, PM2.5, Delhi-NCR, forecasting, weather, dashboard, public health.
