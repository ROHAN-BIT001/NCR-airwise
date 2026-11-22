"""Panel 5: sources, definitions, evaluation results, limitations (Manan)."""
import pandas as pd
import streamlit as st

from app import text
from app.common import load_table
from src.aqi import CATEGORIES


def render():
    st.subheader("5. About and limits")

    st.markdown("**Data sources**")
    for line in text.DATA_SOURCES:
        st.markdown(f"- {line}")

    st.markdown("**AQI categories (CPCB)**")
    st.table(pd.DataFrame(CATEGORIES, columns=["Category", "AQI from", "AQI to"]))
    st.caption(text.AQI_NOTE)

    st.markdown("**Evaluation on the held-out test period**")
    metrics = load_table("metrics.csv")
    if metrics is None:
        st.info("Data unavailable: evaluation has not been run yet (python -m src.train_baselines).")
    else:
        shown = metrics.rename(columns={"cat_accuracy": "category accuracy", "pod_very_poor": "POD (Very Poor+)",
                                        "far_very_poor": "FAR (Very Poor+)", "range_coverage": "range coverage"})
        st.dataframe(shown.round(3), use_container_width=True)
        st.caption("RMSE and MAE are in µg/m³. POD = share of Very Poor+ days that were caught; "
                   "FAR = share of Very Poor+ warnings that were false alarms.")

    st.markdown("**Known limitations**")
    for line in text.LIMITATIONS:
        st.markdown(f"- {line}")
