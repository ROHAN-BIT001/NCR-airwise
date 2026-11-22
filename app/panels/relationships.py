"""Panel 3: pollution-weather relationships (Rohan)."""
import pandas as pd
import plotly.express as px
import streamlit as st

from app import text
from app.common import COLOUR_OBSERVED, unavailable

VARIABLES = {"Wind speed (m/s)": "wind_speed", "Relative humidity (%)": "rh", "Temperature (°C)": "temp"}


def render(daily, station):
    st.subheader("3. Pollution and weather")
    choice = st.selectbox("Weather variable", list(VARIABLES), key="weather_variable")
    column = VARIABLES[choice]
    data = daily.dropna(subset=["pm25", column])
    if len(data) < 30:
        unavailable(f"too few days with both PM2.5 and {choice.lower()} for {station}")
        return

    scatter, box = st.tabs(["Scatter", "Box plot by quartile"])
    with scatter:
        fig = px.scatter(data, x=column, y="pm25", opacity=0.5, color_discrete_sequence=[COLOUR_OBSERVED],
                         labels={column: choice, "pm25": "PM2.5 daily mean (µg/m³)"})
        st.plotly_chart(fig, use_container_width=True)
    with box:
        groups = pd.qcut(data[column], 4, duplicates="drop").astype(str)
        fig = px.box(data.assign(group=groups), x="group", y="pm25", color_discrete_sequence=[COLOUR_OBSERVED],
                     labels={"group": f"{choice} (quartile range)", "pm25": "PM2.5 daily mean (µg/m³)"})
        st.plotly_chart(fig, use_container_width=True)

    rho = data[[column, "pm25"]].corr(method="spearman").iloc[0, 1]
    st.write(f"Rank correlation between PM2.5 and {choice.lower()} for this station: **{rho:.2f}** "
             "(-1 = move in opposite directions, 0 = no pattern, +1 = move together).")
    st.caption(text.CORRELATION_NOTE)
