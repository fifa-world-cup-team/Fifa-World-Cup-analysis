from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

from scripts.promote_model import (
    beats_champion,
    evaluate_model_on_backtest,
    get_latest_candidate_version,
    get_latest_production_version,
    get_run_accuracy,
    passes_quality_gate,
    select_backtest_dataset,
)
from scripts.train_baseline_model import FEATURE_COLUMNS, TARGET_COLUMN


def test_passes_quality_gate_true_above_threshold() -> None:
    assert passes_quality_gate(0.6, threshold=0.5) is True


def test_passes_quality_gate_false_below_threshold() -> None:
    assert passes_quality_gate(0.4, threshold=0.5) is False


def test_get_latest_candidate_version_picks_highest_version_number() -> None:
    client = MagicMock()
    client.get_latest_versions.return_value = [
        SimpleNamespace(version="1"),
        SimpleNamespace(version="3"),
        SimpleNamespace(version="2"),
    ]

    candidate = get_latest_candidate_version(client, "fifa-world-cup-baseline")

    assert candidate.version == "3"
    client.get_latest_versions.assert_called_once_with("fifa-world-cup-baseline", stages=["None"])


def test_get_latest_candidate_version_raises_when_none_found() -> None:
    client = MagicMock()
    client.get_latest_versions.return_value = []

    with pytest.raises(RuntimeError):
        get_latest_candidate_version(client, "fifa-world-cup-baseline")


def test_get_latest_production_version_picks_highest_version_number() -> None:
    client = MagicMock()
    client.get_latest_versions.return_value = [
        SimpleNamespace(version="4"),
        SimpleNamespace(version="2"),
        SimpleNamespace(version="5"),
    ]

    production = get_latest_production_version(client, "fifa-world-cup-baseline")

    assert production.version == "5"
    client.get_latest_versions.assert_called_once_with(
        "fifa-world-cup-baseline", stages=["Production"]
    )


def test_get_latest_production_version_returns_none_when_missing() -> None:
    client = MagicMock()
    client.get_latest_versions.return_value = []

    assert get_latest_production_version(client, "fifa-world-cup-baseline") is None


def test_get_run_accuracy_raises_when_metric_missing() -> None:
    client = MagicMock()
    client.get_run.return_value = SimpleNamespace(data=SimpleNamespace(metrics={}))

    with pytest.raises(RuntimeError):
        get_run_accuracy(client, "run-123")


def _backtest_row(date: str, result: str) -> dict:
    row = {
        "utc_date": date,
        "home_team": "France",
        "away_team": "Brazil",
        "stage": "LAST_16",
        "rank_difference": 3,
        "points_difference": 42.0,
        "home_rank": 2,
        "away_rank": 5,
        "home_fifa_points": 1850.0,
        "away_fifa_points": 1810.0,
        TARGET_COLUMN: result,
    }
    return row


def test_select_backtest_dataset_uses_most_recent_matches() -> None:
    dataset = pd.DataFrame(
        [
            _backtest_row("2026-06-01T00:00:00Z", "home_win"),
            _backtest_row("2026-06-03T00:00:00Z", "away_win"),
            _backtest_row("2026-06-02T00:00:00Z", "draw"),
        ]
    )

    backtest = select_backtest_dataset(dataset, match_count=2)

    assert backtest["utc_date"].tolist() == [
        "2026-06-02T00:00:00Z",
        "2026-06-03T00:00:00Z",
    ]


def test_evaluate_model_on_backtest_returns_accuracy() -> None:
    dataset = pd.DataFrame(
        [
            _backtest_row("2026-06-01T00:00:00Z", "home_win"),
            _backtest_row("2026-06-02T00:00:00Z", "away_win"),
        ]
    )
    model = MagicMock()
    model.predict.return_value = ["home_win", "draw"]

    accuracy = evaluate_model_on_backtest(model, dataset)

    assert accuracy == 0.5
    predicted_features = model.predict.call_args.args[0]
    assert list(predicted_features.columns) == FEATURE_COLUMNS


def test_beats_champion_requires_candidate_to_be_better() -> None:
    assert beats_champion(0.7, 0.6) is True
    assert beats_champion(0.6, 0.6) is False
    assert beats_champion(0.61, 0.6, min_improvement=0.02) is False
    assert beats_champion(0.5, None) is True
