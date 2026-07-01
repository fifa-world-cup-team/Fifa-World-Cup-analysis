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
MODEL_PATH = Path("models/baseline_model.joblib")
CATEGORICAL_FEATURE_COLUMNS = ["home_team", "away_team", "stage"]
NUMERIC_FEATURE_COLUMNS = [
    "rank_difference",
    "points_difference",
    "home_rank",
    "away_rank",
    "home_fifa_points",
    "away_fifa_points",
]
FEATURE_COLUMNS = [*CATEGORICAL_FEATURE_COLUMNS, *NUMERIC_FEATURE_COLUMNS]
TARGET_COLUMN = "result"
RANDOM_STATE = 42


def load_dataset(dataset_path: Path = DATASET_PATH) -> pd.DataFrame:
    if not dataset_path.exists():
        raise RuntimeError(
            f"Missing processed dataset {dataset_path}. "
            "Run scripts/build_training_dataset.py first."
        )

    dataset = pd.read_csv(dataset_path)
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


def main() -> None:
    dataset = load_dataset()
    model, accuracy = train_model(dataset)
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
