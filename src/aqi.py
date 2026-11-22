"""CPCB AQI calculation (Module 2). Uses PM2.5 and PM10 24-hour breakpoints only."""
import numpy as np
import pandas as pd

# (concentration low, concentration high, index low, index high) in ug/m3
BREAKPOINTS = {
    "pm25": [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
             (91, 120, 201, 300), (121, 250, 301, 400), (251, 380, 401, 500)],
    "pm10": [(0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200),
             (251, 350, 201, 300), (351, 430, 301, 400), (431, 510, 401, 500)],
}

# (category name, AQI low, AQI high)
CATEGORIES = [("Good", 0, 50), ("Satisfactory", 51, 100), ("Moderate", 101, 200),
              ("Poor", 201, 300), ("Very Poor", 301, 400), ("Severe", 401, 500)]
CATEGORY_NAMES = [name for name, _, _ in CATEGORIES]
VERY_POOR_INDEX = CATEGORY_NAMES.index("Very Poor")


def sub_index(conc, pollutant):
    """AQI sub-index for one concentration. Returns NaN for missing or negative input."""
    if conc is None or np.isnan(conc) or conc < 0:
        return np.nan
    for bp_lo, bp_hi, i_lo, i_hi in BREAKPOINTS[pollutant]:
        if conc <= bp_hi:
            return (i_hi - i_lo) / (bp_hi - bp_lo) * (conc - bp_lo) + i_lo
    return 500.0


def category_from_aqi(aqi):
    """Name of the CPCB category for an AQI value (NaN if missing)."""
    if aqi is None or np.isnan(aqi):
        return np.nan
    aqi = round(aqi)
    for name, _, high in CATEGORIES:
        if aqi <= high:
            return name
    return "Severe"


def category_index(name):
    """Position of a category (0 = Good ... 5 = Severe); -1 if missing."""
    return CATEGORY_NAMES.index(name) if name in CATEGORY_NAMES else -1


def compute_aqi(pm25, pm10):
    """Daily AQI = the larger of the PM2.5 and PM10 sub-indices (rounded).

    Limitation: the official AQI uses more pollutants (NO2, SO2, CO, O3, ...).
    """
    pm25_idx = pm25.apply(lambda c: sub_index(c, "pm25"))
    pm10_idx = pm10.apply(lambda c: sub_index(c, "pm10"))
    return pd.concat([pm25_idx, pm10_idx], axis=1).max(axis=1).round()


def pm25_category(pm25):
    """Category from the PM2.5 sub-index only. Used to label PM2.5 forecasts."""
    return pm25.apply(lambda c: category_from_aqi(sub_index(c, "pm25")))
