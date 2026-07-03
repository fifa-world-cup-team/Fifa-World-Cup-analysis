import os
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder


DATASET_PATH = Path("data/processed/training_matches.csv")
DVC_POINTER_PATH = Path("data/processed/training_matches.csv.dvc")
MODEL_PATH = Path("models/baseline_model.joblib")
ENV_PATH = Path(".env")
EXPERIMENT_NAME = "fifa-world-cup-baseline"
REGISTERED_MODEL_NAME = "fifa-world-cup-baseline"
CATEGORICAL_FEATURE_COLUMNS = ["home_team", "away_team", "stage"]
NUMERIC_FEATURE_COLUMNS = [
    "rank_difference",
    "points_difference",
    "home_rank",
    "away_rank",
    "home_fifa_points",
    "away_fifa_points",
    "home_elo",
    "away_elo",
    "elo_difference",
    "home_recent_form_points",
    "away_recent_form_points",
    "home_recent_goals_for_avg",
    "away_recent_goals_for_avg",
    "home_recent_goals_against_avg",
    "away_recent_goals_against_avg",
    "home_matches_played_before",
    "away_matches_played_before",
]
FEATURE_COLUMNS = [*CATEGORICAL_FEATURE_COLUMNS, *NUMERIC_FEATURE_COLUMNS]
TARGET_COLUMN = "result"
RANDOM_STATE = 42
DEFAULT_ENGINEERED_FEATURE_VALUES = {
    "home_elo": 1500.0,
    "away_elo": 1500.0,
    "elo_difference": 0.0,
    "home_recent_form_points": 0.0,
    "away_recent_form_points": 0.0,
    "home_recent_goals_for_avg": 0.0,
    "away_recent_goals_for_avg": 0.0,
    "home_recent_goals_against_avg": 0.0,
    "away_recent_goals_against_avg": 0.0,
    "home_matches_played_before": 0.0,
    "away_matches_played_before": 0.0,
}


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        name, value = clean_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def get_git_commit_hash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_dvc_data_version(dvc_pointer_path: Path = DVC_POINTER_PATH) -> str:
    if not dvc_pointer_path.exists():
        return "unknown"

    for line in dvc_pointer_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip().lstrip("- ").strip()
        if clean_line.startswith("md5:"):
            return clean_line.split(":", 1)[1].strip()

    return "unknown"


def add_default_engineered_features(dataset: pd.DataFrame) -> pd.DataFrame:
    dataset = dataset.copy()
    for column, default_value in DEFAULT_ENGINEERED_FEATURE_VALUES.items():
        if column not in dataset.columns:
            dataset[column] = default_value
    return dataset


def load_dataset(dataset_path: Path = DATASET_PATH) -> pd.DataFrame:
    if not dataset_path.exists():
        raise RuntimeError(
            f"Missing processed dataset {dataset_path}. "
            "Run scripts/build_training_dataset.py first."
        )

    dataset = add_default_engineered_features(pd.read_csv(dataset_path))
    missing_columns = [
        column
        for column in [*FEATURE_COLUMNS, TARGET_COLUMN]
        if column not in dataset.columns
    ]
    if missing_columns:
        raise RuntimeError(
            "Processed dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    dataset = dataset.dropna(subset=[*FEATURE_COLUMNS, TARGET_COLUMN])
    if dataset.empty:
        raise RuntimeError("Processed dataset does not contain usable rows.")

    return dataset


def train_model(dataset: pd.DataFrame) -> tuple[Pipeline, float]:
    dataset = add_default_engineered_features(dataset)
    x = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    if y.nunique() < 2:
        raise RuntimeError("At least two result classes are required to train a model.")

    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    model = Pipeline(
        steps=[
            (
                "features",
                ColumnTransformer(
                    transformers=[
                        (
                            "categorical",
                            OneHotEncoder(handle_unknown="ignore"),
                            CATEGORICAL_FEATURE_COLUMNS,
                        ),
                        (
                            "numeric",
                            StandardScaler(),
                            NUMERIC_FEATURE_COLUMNS,
                        )
                    ]
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            ),
        ]
    )

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    return model, accuracy


def save_model(model: Pipeline, model_path: Path = MODEL_PATH) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def log_model_to_mlflow(model: Pipeline, accuracy: float, tracking_uri: str | None) -> None:
    try:
        import mlflow
        import mlflow.sklearn
    except ImportError as error:
        print(f"Warning: MLflow logging skipped ({error}).", file=sys.stderr)
        return

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("categorical_features", ",".join(CATEGORICAL_FEATURE_COLUMNS))
        mlflow.log_param("numeric_features", ",".join(NUMERIC_FEATURE_COLUMNS))
        mlflow.log_param("git_commit", get_git_commit_hash())
        mlflow.log_param("dvc_data_version", get_dvc_data_version())
        mlflow.log_metric("accuracy", accuracy)

        log_model_kwargs = {"artifact_path": "model"}
        if tracking_uri:
            log_model_kwargs["registered_model_name"] = REGISTERED_MODEL_NAME
        mlflow.sklearn.log_model(model, **log_model_kwargs)


def main() -> None:
    load_env_file()
    dataset = load_dataset()

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    model, accuracy = train_model(dataset)
    log_model_to_mlflow(model, accuracy, tracking_uri)
    save_model(model)

    print(f"Trained baseline model on {len(dataset)} matches")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
