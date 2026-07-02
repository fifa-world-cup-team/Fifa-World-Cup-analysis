from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts.promote_model import (
    get_latest_candidate_version,
    get_run_accuracy,
    passes_quality_gate,
)


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


def test_get_run_accuracy_raises_when_metric_missing() -> None:
    client = MagicMock()
    client.get_run.return_value = SimpleNamespace(data=SimpleNamespace(metrics={}))

    with pytest.raises(RuntimeError):
        get_run_accuracy(client, "run-123")
