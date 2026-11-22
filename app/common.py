"""Shared helpers for the dashboard: data loading, colours, labels."""
import pandas as pd
import streamlit as st

from src.aqi import BREAKPOINTS
from src.config import PROCESSED_DIR

COLOUR_OBSERVED = "#1f77b4"  # blue = observed data
COLOUR_MODEL = "#d62728"     # red = the team's own model output
CATEGORY_COLOURS = {"Good": "#00b050", "Satisfactory": "#92d050", "Moderate": "#ffc000",
                    "Poor": "#ff7c00", "Very Poor": "#ff0000", "Severe": "#c00000"}


@st.cache_data
def load_table(filename, date_columns=()):
    """Read a CSV from data/processed. Returns None if the file does not exist yet."""
    path = PROCESSED_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path, parse_dates=list(date_columns))


def pm25_bands():
    """PM2.5 concentration limits of each AQI category, for shading charts: [(name, low, high)]."""
    names = list(CATEGORY_COLOURS)
    bands = BREAKPOINTS["pm25"]
    return [(name, 0 if i == 0 else bands[i - 1][1], bands[i][1]) for i, name in enumerate(names)]


def unavailable(what):
    st.info(f"Data unavailable: {what}. Run the data pipeline (see README) or choose another station.")
