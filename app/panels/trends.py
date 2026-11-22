"""Panel 2: PM2.5 trend with AQI category bands (Rohan)."""
import plotly.graph_objects as go
import streamlit as st

from app import text
from app.common import CATEGORY_COLOURS, COLOUR_OBSERVED, pm25_bands, unavailable


def render(daily, station):
    st.subheader("2. Trends")
    data = daily.dropna(subset=["pm25"])
    if data.empty:
        unavailable(f"no PM2.5 readings for {station} in the selected dates")
        return
    top = max(data["pm25"].max() * 1.05, 260)
    fig = go.Figure()
    for name, low, high in pm25_bands():
        fig.add_hrect(y0=low, y1=min(high, top) if name != "Severe" else top,
                      fillcolor=CATEGORY_COLOURS[name], opacity=0.15, line_width=0,
                      annotation_text=name, annotation_position="right")
    fig.add_trace(go.Scatter(x=data["date"], y=data["pm25"], mode="lines",
                             name=text.LABEL_OBSERVED, line={"color": COLOUR_OBSERVED}))
    fig.update_layout(yaxis_title="PM2.5 daily mean (µg/m³)", xaxis_title="Date",
                      yaxis_range=[0, top], height=420, margin={"r": 100})
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{text.LABEL_OBSERVED} data. Shaded bands are the CPCB categories for PM2.5.")
