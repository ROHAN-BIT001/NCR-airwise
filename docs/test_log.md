# Test log (Rohan)

All results below were observed on 22 November 2026, on the final `main` branch, with the real data (`daily_features.csv` built from the Kaggle CPCB data 2015 to mid-2020 and Open-Meteo weather).

## Automated tests

Command: `python -m pytest -v` (output saved in `docs/evidence/pytest_output.txt`).
Result: **19 passed**, 0 failed. Three warnings come from a pandas deprecation notice about `dayofweek` in `src/features.py`; they do not affect results.

| Test | Check | Run date | Result | Evidence |
| --- | --- | --- | --- | --- |
| T1 Timestamp alignment | `tests/test_cleaning.py::test_merge_has_no_duplicate_or_shifted_hours` | 22 Nov 2026 | Passed | `docs/evidence/pytest_output.txt` |
| T2 AQI function | `tests/test_aqi.py` (5 tests: PM2.5 and PM10 band edges, category boundaries, missing and negative inputs, AQI is the larger sub-index) | 22 Nov 2026 | Passed (5 of 5) | `docs/evidence/pytest_output.txt` |
| T3 Missing data | `tests/test_cleaning.py::test_missing_share_reported_per_station` | 22 Nov 2026 | Passed. The real report is `data/processed/missing_report.csv`: PM2.5 missing is 21.1% (Anand Vihar), 1.3% (Dwarka Sector 8), 55.3% (ITO), 25.4% (Punjabi Bagh), 20.1% (RK Puram) | `docs/evidence/pytest_output.txt`, `docs/data_sources.md` |
| T4 No leakage | `tests/test_evaluation.py::test_test_period_is_strictly_after_training` | 22 Nov 2026 | Passed. The real split starts validation on 2018-11-07 and the test block on 2019-07-23, after all training dates | `docs/evidence/pytest_output.txt` |
| T5 Baseline comparison | `data/processed/metrics.csv` | 22 Nov 2026 | Done. Averaged over the five stations, ridge has the lowest RMSE at 1 day (48.4 against 50.7 for persistence) and at 2 days (60.8 against 67.8). Climatology is worst (about 85). MAE is about equal at 1 day. Persistence is slightly better at Dwarka Sector 8 for 1 day. Details in `docs/data_sources.md` | `data/processed/metrics.csv` |

Other tests in the suite that also passed: UTC to IST conversion, removal of negative and huge values, only short gaps filled, daily mean needs enough hours, lag and target use calendar days, a missing day is not skipped, rolling mean uses only past data, split blocks do not overlap, regression metrics, POD and FAR, and the forecast range is never below zero.

## Manual tests (dashboard)

Command: `python -m streamlit run app/streamlit_app.py` on the real data and the real baseline result files.

| Test | Check | Run date | Result | Evidence |
| --- | --- | --- | --- | --- |
| T6 Dashboard rendering | Each panel for 3 stations, including one with many gaps (ITO) and one with a short history (Dwarka Sector 8) | 22 Nov 2026 | All five panels rendered for Anand Vihar, ITO and Dwarka Sector 8 without error messages. Current status shows the latest day with enough data (2020-06-30 for Anand Vihar), not today's date | `docs/evidence/t6_anand_vihar_top.png`, `t6_anand_vihar_bottom.png`, `t6_ito_top.png`, `t6_ito_bottom.png`, `t6_dwarka_top.png`, `t6_dwarka_bottom.png` |
| T7 Labelling | Screenshots show Observed versus Model prediction labels and colours | 22 Nov 2026 | Observed data is blue and labelled "Observed". The team's forecast is red and labelled "Model prediction (team's own)", with a shaded forecast range. The disclaimer "Student prototype, not an official forecast" is shown at the top of the page | `docs/evidence/t7_forecast_labels.png` |

## Observations

- The latest forecast is for 1 and 2 July 2020, because the data ends in mid-2020. It is not a forecast for today.
- The forecast ranges are wide (the lower bound is often 0). They are 90% ranges from validation errors that include a winter.
- ITO has more than half of its PM2.5 values missing, so its trend line has gaps. Dwarka Sector 8 has data only from February 2018.
- Known limitation: AQI here uses only PM2.5 and PM10, so it can differ from official AQI reports.
