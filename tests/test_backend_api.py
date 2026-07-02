import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app, app_state
from scripts.train_baseline_model import train_model

RANKINGS = pd.DataFrame(
    [
        {"country": "France", "confederation": "UEFA", "rank": 3, "fifa_points": 1870.7},
        {"country": "Argentina", "confederation": "CONMEBOL", "rank": 1, "fifa_points": 1877.3},
    ]
)


def _train_stub_model():
    def row(home_team, away_team, stage, result, home_rank, away_rank, home_points, away_points):
        return {
            "home_team": home_team,
            "away_team": away_team,
            "stage": stage,
            "result": result,
            "home_rank": home_rank,
            "away_rank": away_rank,
            "home_fifa_points": home_points,
            "away_fifa_points": away_points,
            "rank_difference": away_rank - home_rank,
            "points_difference": home_points - away_points,
        }

    dataset = pd.DataFrame(
        [
            row("France", "Argentina", "GROUP_STAGE", "home_win", 3, 1, 1870.7, 1877.3),
            row("Brazil", "Spain", "GROUP_STAGE", "draw", 6, 2, 1761.0, 1874.7),
            row("Germany", "Italy", "GROUP_STAGE", "away_win", 10, 9, 1717.0, 1718.0),
            row("France", "Brazil", "ROUND_OF_16", "home_win", 3, 6, 1870.7, 1761.0),
        ]
    )
    model, _ = train_model(dataset)
    return model


def test_health_reports_degraded_when_model_not_loaded() -> None:
    app_state.update({"model": None, "model_uri": None, "rankings": None, "error": "no model"})
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "degraded", "model_uri": None, "detail": "no model"}


def test_predict_returns_503_when_model_not_loaded() -> None:
    app_state.update({"model": None, "model_uri": None, "rankings": None, "error": "no model"})
    client = TestClient(app)

    response = client.post(
        "/predict",
        json={"home_team": "France", "away_team": "Argentina"},
    )

    assert response.status_code == 503


def test_predict_returns_prediction_when_model_loaded() -> None:
    app_state.update(
        {
            "model": _train_stub_model(),
            "model_uri": "models:/fifa-world-cup-baseline/1",
            "rankings": RANKINGS,
            "error": None,
        }
    )
    client = TestClient(app)

    response = client.post(
        "/predict",
        json={"home_team": "France", "away_team": "Argentina", "stage": "GROUP_STAGE"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in {"home_win", "draw", "away_win"}
    assert abs(sum(body["probabilities"].values()) - 1) < 1e-6


def test_predict_returns_422_for_unknown_team() -> None:
    app_state.update(
        {
            "model": _train_stub_model(),
            "model_uri": "models:/fifa-world-cup-baseline/1",
            "rankings": RANKINGS,
            "error": None,
        }
    )
    client = TestClient(app)

    response = client.post(
        "/predict",
        json={"home_team": "Narnia", "away_team": "Argentina"},
    )

    assert response.status_code == 422
