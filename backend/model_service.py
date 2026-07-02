import os
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.tracking import MlflowClient
from sklearn.pipeline import Pipeline

from scripts.build_training_dataset import RANKING_COLUMNS, normalize_team_name
from scripts.train_baseline_model import FEATURE_COLUMNS

MODEL_NAME = "fifa-world-cup-baseline"
RANKINGS_PATH = Path("data/processed/fifa_rankings_current.csv")
ENV_PATH = Path(".env")


class PredictionError(Exception):
    pass


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        name, value = clean_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def resolve_model_uri(client: MlflowClient, model_name: str, stage: str) -> str:
    versions = client.get_latest_versions(model_name, stages=[stage])
    if versions:
        return f"models:/{model_name}/{stage}"

    all_versions = client.search_model_versions(f"name='{model_name}'")
    if not all_versions:
        raise PredictionError(f"No registered versions found for model '{model_name}'.")

    latest = max(all_versions, key=lambda version: int(version.version))
    return f"models:/{model_name}/{latest.version}"


def load_model() -> tuple[Pipeline, str]:
    load_env_file()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    stage = os.getenv("MODEL_STAGE", "None")
    client = MlflowClient()
    model_uri = resolve_model_uri(client, MODEL_NAME, stage)
    model = mlflow.sklearn.load_model(model_uri)
    return model, model_uri


def load_rankings(rankings_path: Path = RANKINGS_PATH) -> pd.DataFrame:
    if not rankings_path.exists():
        raise PredictionError(f"Missing rankings file {rankings_path}.")

    rankings = pd.read_csv(rankings_path)
    return rankings[RANKING_COLUMNS].drop_duplicates(subset=["country"])


def build_feature_row(
    home_team: str,
    away_team: str,
    stage: str,
    rankings: pd.DataFrame,
) -> pd.DataFrame:
    def lookup_ranking(team_name: str) -> pd.Series:
        mapped_name = normalize_team_name(team_name)
        matches = rankings.loc[rankings["country"] == mapped_name]
        if matches.empty:
            raise PredictionError(f"No FIFA ranking found for team '{team_name}'.")
        return matches.iloc[0]

    home_ranking = lookup_ranking(home_team)
    away_ranking = lookup_ranking(away_team)

    row = pd.DataFrame(
        [
            {
                "home_team": home_team,
                "away_team": away_team,
                "stage": stage,
                "home_rank": home_ranking["rank"],
                "away_rank": away_ranking["rank"],
                "home_fifa_points": home_ranking["fifa_points"],
                "away_fifa_points": away_ranking["fifa_points"],
                "rank_difference": away_ranking["rank"] - home_ranking["rank"],
                "points_difference": home_ranking["fifa_points"] - away_ranking["fifa_points"],
            }
        ]
    )
    return row[FEATURE_COLUMNS]


def predict_match(
    model: Pipeline,
    rankings: pd.DataFrame,
    home_team: str,
    away_team: str,
    stage: str,
) -> dict:
    features = build_feature_row(home_team, away_team, stage, rankings)
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    classes = model.named_steps["classifier"].classes_

    return {
        "prediction": prediction,
        "probabilities": dict(zip(classes, (float(p) for p in probabilities))),
    }
