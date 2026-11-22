"""NCR AIRWISE dashboard. Run from the project root:  streamlit run app/streamlit_app.py"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # lets us import src and app

import streamlit as st  # noqa: E402

from app import text  # noqa: E402
from app.common import load_table, unavailable  # noqa: E402
from app.panels import about, forecast, relationships, status, trends  # noqa: E402

st.set_page_config(page_title="NCR AIRWISE", layout="wide")
st.title("NCR AIRWISE")
st.warning(text.DISCLAIMER)

daily = load_table("daily_features.csv", ["date"])
if daily is None:
    unavailable("data/processed/daily_features.csv not found (run python -m src.build_dataset)")
    st.stop()

stations = sorted(daily["station"].unique())
station = st.sidebar.selectbox("Station", stations, format_func=str.title)
station_data = daily[daily["station"] == station]
first, last = station_data["date"].min().date(), station_data["date"].max().date()
picked = st.sidebar.date_input("Date range", (first, last), min_value=first, max_value=last)
if len(picked) != 2:
    st.info("Pick both a start and an end date in the sidebar.")
    st.stop()
start, end = picked
selected = station_data[(station_data["date"].dt.date >= start) & (station_data["date"].dt.date <= end)]

status.render(station_data, station)  # status always shows the newest data
trends.render(selected, station)
relationships.render(selected, station)
forecast.render(station)
about.render()
