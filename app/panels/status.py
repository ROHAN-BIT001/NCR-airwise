"""Panel 1: latest observed status (Rohan)."""
import pandas as pd
import streamlit as st

from app import text
from app.common import CATEGORY_COLOURS, unavailable


def show(value, unit, digits=0):
    """Format a number for display, or 'n/a' when the value is missing."""
    return "n/a" if pd.isna(value) else f"{value:.{digits}f} {unit}".strip()


def render(daily, station):
    st.subheader("1. Current status")
    data = daily.dropna(subset=["pm25"])
    if data.empty:
        unavailable(f"no PM2.5 readings for {station}")
        return
    latest = data.iloc[-1]
    category = latest["aqi_category"]
    st.caption(f"{text.LABEL_OBSERVED} | source: CPCB station data, Open-Meteo weather | "
               f"latest day with enough data: {latest['date'].date()}")

    cols = st.columns(4)
    cols[0].metric("PM2.5 (daily mean)", show(latest["pm25"], "µg/m³"))
    cols[1].metric("AQI", show(latest["aqi"], ""))
    cols[2].metric("Temperature", show(latest["temp"], "°C", 1))
    cols[3].metric("Wind speed", show(latest["wind_speed"], "m/s", 1))
    if isinstance(category, str):
        colour = CATEGORY_COLOURS.get(category, "#888888")
        st.markdown(f"AQI category: <span style='color:{colour};font-weight:bold'>{category}</span>",
                    unsafe_allow_html=True)
    st.caption(text.AQI_NOTE)
