"""Baseline forecasting models (Module 3). Every model has fit(df, target) and predict(df)."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.features import FEATURE_COLS


class Persistence:
    """Forecast = today's PM2.5."""
    name = "persistence"

    def fit(self, df, target):
        return self

    def predict(self, df):
        return df["pm25"].to_numpy()


class Climatology:
    """Forecast = average target value for that calendar month in the training years."""
    name = "climatology"

    def fit(self, df, target):
        self.by_month = df.groupby("month")[target].mean()
        self.overall = df[target].mean()
        return self

    def predict(self, df):
        return df["month"].map(self.by_month).fillna(self.overall).to_numpy()


class RidgeModel:
    """Linear regression with a penalty, on lag, weather and calendar features."""
    name = "ridge"

    def fit(self, df, target):
        self.model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
        self.model.fit(df[FEATURE_COLS], df[target])
        return self

    def predict(self, df):
        return np.clip(self.model.predict(df[FEATURE_COLS]), 0, None)  # PM2.5 cannot be negative


class ForestModel:
    """Stretch model for Milestone 3 (switch on with --with-forest)."""
    name = "random_forest"

    def fit(self, df, target):
        self.model = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42)
        self.model.fit(df[FEATURE_COLS], df[target])
        return self

    def predict(self, df):
        return self.model.predict(df[FEATURE_COLS])


def baseline_models(with_forest=False):
    models = [Persistence(), Climatology(), RidgeModel()]
    return models + [ForestModel()] if with_forest else models
