from pathlib import Path

import pandas as pd

from scripts.build_training_dataset import build_training_dataset, load_csv
from scripts.preprocess_matches import build_processed_rows, load_raw_matches
from scripts.train_baseline_model import FEATURE_COLUMNS, train_model

RAW_MATCHES_FIXTURE = Path("tests/fixtures/raw_matches_sample.json")
RANKINGS_FIXTURE = Path("tests/fixtures/rankings_sample.csv")


def test_full_pipeline_from_raw_matches_to_prediction() -> None:
    """Exercises the whole system end to end: raw match data + FIFA
    rankings on disk -> preprocessing -> feature engineering -> model
    training -> a live prediction, the same journey the app is meant
    to serve once it has an API in front of it.
    """
    raw_matches = load_raw_matches(RAW_MATCHES_FIXTURE)
    processed_rows = build_processed_rows(raw_matches)
    matches = pd.DataFrame(processed_rows)

    rankings = load_csv(RANKINGS_FIXTURE, "FIFA rankings")

    training_dataset = build_training_dataset(matches, rankings)
    model, accuracy = train_model(training_dataset)

    assert 0 <= accuracy <= 1

    upcoming_match = training_dataset.iloc[[0]][FEATURE_COLUMNS]
    prediction = model.predict(upcoming_match)
    probabilities = model.predict_proba(upcoming_match)

    assert prediction[0] in {"home_win", "draw", "away_win"}
    assert probabilities.shape == (1, len(model.named_steps["classifier"].classes_))
    assert abs(probabilities.sum() - 1) < 1e-6
