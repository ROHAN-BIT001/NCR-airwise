"""Panel 4: the team's own forecast (Manan). Reads latest_forecast.csv and test_predictions.csv."""
import plotly.graph_objects as go
import streamlit as st

from app import text
from app.common import COLOUR_MODEL, COLOUR_OBSERVED, load_table, unavailable

DEFAULT_MODEL = "ridge"


def render(station):
    st.subheader("4. Forecast")
    st.markdown(f"**:red[{text.LABEL_MODEL}]**")
    latest = load_table("latest_forecast.csv", ["issue_date", "target_date"])
    history = load_table("test_predictions.csv", ["date"])
    if latest is None or history is None:
        unavailable("no model output yet (run python -m src.train_baselines)")
        return

    latest = latest[(latest["station"] == station) & (latest["model"] == DEFAULT_MODEL)]
    if latest.empty:
        unavailable(f"no forecast for {station} (too little data to train a model)")
        return

    cols = st.columns(len(latest))
    for col, (_, row) in zip(cols, latest.sort_values("horizon").iterrows()):
        col.metric(f"{row['target_date'].date()} (+{row['horizon']} day)", f"{row['predicted']:.0f} µg/m³",
                   help=f"Range {row['lower']:.0f} to {row['upper']:.0f} µg/m³")
        col.write(f"Range: {row['lower']:.0f} to {row['upper']:.0f} µg/m³")
        col.write(f"Category: {row['category']}")
    st.caption(f"Forecast issued from data up to {latest['issue_date'].iloc[0].date()}. {text.FORECAST_NOTE}")

    st.markdown("**Past test period: observed versus predicted**")
    options = sorted(history.loc[history["station"] == station, "model"].unique())
    if not options:
        unavailable(f"no test-period predictions for {station}")
        return
    left, right = st.columns(2)
    model = left.selectbox("Model", options, index=options.index(DEFAULT_MODEL) if DEFAULT_MODEL in options else 0)
    horizon = right.selectbox("Days ahead", sorted(history["horizon"].unique()))
    data = history[(history["station"] == station) & (history["model"] == model)
                   & (history["horizon"] == horizon)].sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["date"], y=data["upper"], line={"width": 0}, showlegend=False))
    fig.add_trace(go.Scatter(x=data["date"], y=data["lower"], fill="tonexty", line={"width": 0},
                             fillcolor="rgba(214,39,40,0.15)", name="Forecast range"))
    fig.add_trace(go.Scatter(x=data["date"], y=data["predicted"], name=text.LABEL_MODEL,
                             line={"color": COLOUR_MODEL, "dash": "dash"}))
    fig.add_trace(go.Scatter(x=data["date"], y=data["observed"], name=text.LABEL_OBSERVED,
                             line={"color": COLOUR_OBSERVED}))
    fig.update_layout(yaxis_title="PM2.5 daily mean (µg/m³)", height=420)
    st.plotly_chart(fig, use_container_width=True)
