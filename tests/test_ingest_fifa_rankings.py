import os

import pytest

from scripts.ingest_fifa_rankings import (
    build_current_ranking_url,
    get_required_api_key,
)


def test_build_current_ranking_url() -> None:
    url = build_current_ranking_url(
        "https://world-football-ranking.p.rapidapi.com/",
        "live",
    )

    assert (
        url
        == "https://world-football-ranking.p.rapidapi.com/current-ranking.php?type=live"
    )


def test_get_required_api_key_reads_primary_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORLD_FOOTBALL_RANKING_API_KEY", "test-key")
    monkeypatch.delenv("X_RAPIDAPI_KEY", raising=False)
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)

    assert get_required_api_key() == "test-key"


def test_get_required_api_key_fails_without_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "WORLD_FOOTBALL_RANKING_API_KEY",
        "X_RAPIDAPI_KEY",
        "RAPIDAPI_KEY",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError):
        get_required_api_key()
