import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app, app_state
from backend.model_service import PredictionError, load_local_model, remove_draw_for_knockout
from scripts.train_baseline_model import train_model

RANKINGS = pd.DataFrame(
    [
        {"country": "France", "confederation": "UEFA", "rank": 3, "rank_change": -2, "fifa_points": 1870.7, "points_change": -6.6},
        {"country": "Argentina", "confederation": "CONMEBOL", "rank": 1, "rank_change": 2, "fifa_points": 1877.3, "points_change": 2.5},
    ]
)


def _train_stub_model():
    def row(home, away, stage, result, hr, ar, hp, ap):
        return {
            "home_team": home, "away_team": away, "stage": stage, "result": result,
            "home_rank": hr, "away_rank": ar,
            "home_fifa_points": hp, "away_fifa_points": ap,
            "rank_difference": ar - hr, "points_difference": hp - ap,
        }

    dataset = pd.DataFrame([
        row("France", "Argentina", "GROUP_STAGE", "home_win", 3, 1, 1870.7, 1877.3),
        row("Brazil", "Spain", "GROUP_STAGE", "draw", 6, 2, 1761.0, 1874.7),
        row("Germany", "Italy", "GROUP_STAGE", "away_win", 10, 9, 1717.0, 1718.0),
        row("France", "Brazil", "SEMI_FINALS", "home_win", 3, 6, 1870.7, 1761.0),
    ])
    model, _ = train_model(dataset)
    return model


def _loaded_state():
    return {"model": _train_stub_model(), "model_uri": "local:models/stub", "rankings": RANKINGS, "error": None}


def test_health_returns_ok_when_model_is_loaded() -> None:
    app_state.update(_loaded_state())
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["detail"] is None


def test_predict_missing_required_field_returns_422() -> None:
    app_state.update(_loaded_state())
    client = TestClient(app)

    # home_team is missing
    response = client.post("/predict", json={"away_team": "Argentina"})

    assert response.status_code == 422


def test_predict_knockout_stage_has_zero_draw_probability() -> None:
    app_state.update(_loaded_state())
    client = TestClient(app)

    response = client.post(
        "/predict",
        json={"home_team": "France", "away_team": "Argentina", "stage": "SEMI_FINALS"},
    )

    assert response.status_code == 200
    assert response.json()["probabilities"]["draw"] == 0.0


def test_predict_probabilities_are_each_between_0_and_1() -> None:
    app_state.update(_loaded_state())
    client = TestClient(app)

    response = client.post(
        "/predict",
        json={"home_team": "France", "away_team": "Argentina", "stage": "GROUP_STAGE"},
    )

    assert response.status_code == 200
    for label, value in response.json()["probabilities"].items():
        assert 0.0 <= value <= 1.0, f"probability for '{label}' out of range: {value}"


def test_predict_failure_counter_increments_on_unknown_team() -> None:
    app_state.update(_loaded_state())
    client = TestClient(app)

    before_text = client.get("/metrics").text
    before_count = float(
        next(
            line.split()[-1]
            for line in before_text.splitlines()
            if line.startswith("prediction_failures_total ")
        )
    )

    client.post("/predict", json={"home_team": "Atlantis", "away_team": "Argentina"})

    after_text = client.get("/metrics").text
    after_count = float(
        next(
            line.split()[-1]
            for line in after_text.splitlines()
            if line.startswith("prediction_failures_total ")
        )
    )

    assert after_count == before_count + 1


def test_remove_draw_for_knockout_returns_equal_split_when_wins_are_zero() -> None:
    probabilities = {"home_win": 0.0, "draw": 1.0, "away_win": 0.0}

    result = remove_draw_for_knockout(probabilities, "FINAL")

    assert result["draw"] == 0.0
    assert result["home_win"] == 0.5
    assert result["away_win"] == 0.5


def test_load_local_model_raises_when_file_does_not_exist(tmp_path) -> None:
    missing_path = tmp_path / "nonexistent_model.joblib"

    with pytest.raises(PredictionError, match="missing"):
        load_local_model(missing_path)
