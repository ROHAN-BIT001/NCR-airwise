"""T2: known concentrations map to the correct CPCB category."""
import numpy as np
import pandas as pd

from src.aqi import category_from_aqi, compute_aqi, sub_index


def test_pm25_band_edges():
    expected = {0: 0, 30: 50, 31: 51, 60: 100, 61: 101, 90: 200, 91: 201,
                120: 300, 121: 301, 250: 400, 251: 401}
    for conc, aqi in expected.items():
        assert round(sub_index(conc, "pm25")) == aqi, conc


def test_pm10_band_edges():
    expected = {50: 50, 51: 51, 100: 100, 101: 101, 250: 200, 251: 201, 350: 300, 351: 301, 430: 400, 431: 401}
    for conc, aqi in expected.items():
        assert round(sub_index(conc, "pm10")) == aqi, conc


def test_category_boundaries():
    cases = {0: "Good", 50: "Good", 51: "Satisfactory", 100: "Satisfactory", 101: "Moderate",
             200: "Moderate", 201: "Poor", 300: "Poor", 301: "Very Poor", 400: "Very Poor",
             401: "Severe", 500: "Severe"}
    for aqi, name in cases.items():
        assert category_from_aqi(aqi) == name, aqi


def test_missing_and_negative_inputs():
    assert np.isnan(sub_index(np.nan, "pm25"))
    assert np.isnan(sub_index(-5, "pm25"))
    assert np.isnan(category_from_aqi(np.nan))


def test_aqi_is_larger_sub_index():
    aqi = compute_aqi(pd.Series([30.0, np.nan]), pd.Series([300.0, 60.0]))
    assert aqi.iloc[0] == round(sub_index(300.0, "pm10"))  # PM10 dominates in row 0
    assert aqi.iloc[1] == round(sub_index(60.0, "pm10"))  # PM2.5 missing: PM10 only
