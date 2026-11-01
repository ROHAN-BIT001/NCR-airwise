"""Central settings. Change values here, not inside the other files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_AIR_DIR = ROOT / "data" / "raw" / "cpcb"
RAW_WEATHER_DIR = ROOT / "data" / "raw" / "weather"
PROCESSED_DIR = ROOT / "data" / "processed"

# Stations used by the project: name -> (latitude, longitude).
# Coordinates are approximate. Udbhav confirms the final list after checking which
# stations have the most complete records, and documents the choice in docs/data_sources.md.
STATIONS = {
    "Anand Vihar": (28.6469, 77.3158),
    "RK Puram": (28.5633, 77.1869),
    "Punjabi Bagh": (28.6742, 77.1330),
    "ITO": (28.6286, 77.2410),
    "Dwarka Sector 8": (28.5710, 77.0719),
}

# Raw CSV column names we accept (lower-case) -> the standard name used in the code.
COLUMN_ALIASES = {
    "station": "station",
    "site": "station",
    "station name": "station",
    "datetime": "datetime",
    "timestamp": "datetime",
    "from date": "datetime",
    "date": "datetime",
    "time": "datetime",
    "pm2.5": "pm25",
    "pm2.5 (ug/m3)": "pm25",
    "pm2.5 (µg/m³)": "pm25",
    "pm25": "pm25",
    "pm10": "pm10",
    "pm10 (ug/m3)": "pm10",
    "pm10 (µg/m³)": "pm10",
}
DAYFIRST = True  # CPCB exports use dd-mm-yyyy dates

# Cleaning rules
MAX_VALID = {"pm25": 1500.0, "pm10": 2500.0}  # above this value = physically implausible
MAX_INTERPOLATE_HOURS = 3  # only gaps up to this many hours are filled
MIN_HOURS_PER_DAY = 18  # a daily mean needs at least this many valid hours
OUTLIER_MAD_FACTOR = 10  # flag (never delete) values this many robust SDs above the median

# Modelling
HORIZONS = (1, 2)  # forecast 1 and 2 days ahead
# Dates are split in time order: oldest = train, then validation, newest = test.
VAL_FRACTION = 0.15  # 15% of dates (just before the test block) used for forecast ranges
TEST_FRACTION = 0.20  # newest 20% of dates used only for final scoring
MIN_TRAIN_ROWS = 60  # skip a station with fewer usable training days
INTERVAL_LOW, INTERVAL_HIGH = 0.05, 0.95  # 90% forecast range from validation residuals
