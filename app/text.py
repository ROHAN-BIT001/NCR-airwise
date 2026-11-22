"""All wording shown in the dashboard (Manan). Edit text here, not inside the panels."""

DISCLAIMER = "Student prototype, not an official forecast. No health advice is given."

LABEL_OBSERVED = "Observed"
LABEL_MODEL = "Model prediction (team's own)"

CORRELATION_NOTE = (
    "These charts show how PM2.5 and weather move together in past data. "
    "Correlation is not causation: low wind and high pollution often occur together, "
    "but the charts alone cannot prove that one causes the other."
)

AQI_NOTE = (
    "AQI here is calculated from PM2.5 and PM10 only, using CPCB category bands. "
    "The official AQI also uses other pollutants, so values can differ from official reports."
)

FORECAST_NOTE = (
    "Forecasts come from simple models trained on past data. The shaded range is built from the "
    "model's own past errors on data it had not seen, so real values can still fall outside it."
)

LIMITATIONS = [
    "Not an official alert system; official sources such as CPCB, SAFAR and AQEWS should be used for decisions.",
    "Data gaps and sensor errors limit model quality. The team does not expect to beat official systems.",
    "Stubble-burning is represented only by a month-based season flag; no fire-count data is used yet.",
    "Models use today's observed weather, not weather forecasts, so they cannot anticipate coming weather changes.",
    "Only aggregated environmental data is used. No personal data is collected.",
]

DATA_SOURCES = [
    "Air quality: public CPCB station data for Delhi-NCR (downloaded by the team).",
    "Weather: Open-Meteo historical weather API.",
]
