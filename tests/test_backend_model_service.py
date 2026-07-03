import pandas as pd
import pytest

from backend.model_service import (
    PredictionError,
    build_feature_row,
    load_local_model,
    predict_match,
)
from scripts.train_baseline_model import FEATURE_COLUMNS, train_model

RANKINGS = pd.DataFrame(
    [
        {"country": "France", "confederation": "UEFA", "rank": 3, "rank_change": -2, "fifa_points": 1870.7, "points_change": -6.6},
        {"country": "Argentina", "confederation": "CONMEBOL", "rank": 1, "rank_change": 2, "fifa_points": 1877.3, "points_change": 2.5},
    ]
)


def test_build_feature_row_computes_rank_and_points_difference() -> None:
    row = build_feature_row("France", "Argentina", "GROUP_STAGE", RANKINGS)

    assert list(row.columns) == FEATURE_COLUMNS
    assert row.iloc[0]["home_rank"] == 3
    assert row.iloc[0]["away_rank"] == 1
    assert row.iloc[0]["rank_difference"] == -2
    assert round(row.iloc[0]["points_difference"], 1) == -6.6
    assert row.iloc[0]["home_elo"] == 1500.0
    assert row.iloc[0]["away_elo"] == 1500.0
    assert row.iloc[0]["elo_difference"] == 0.0
    assert row.iloc[0]["home_recent_form_points"] == 0.0
    assert row.iloc[0]["away_recent_goals_for_avg"] == 0.0


def test_build_feature_row_raises_for_unknown_team() -> None:
    with pytest.raises(PredictionError):
        build_feature_row("Narnia", "Argentina", "GROUP_STAGE", RANKINGS)


def test_load_local_model_returns_joblib_model(tmp_path) -> None:
    model_path = tmp_path / "baseline_model.joblib"
    dataset = pd.DataFrame(
        [
            {
                "home_team": "France",
                "away_team": "Argentina",
                "stage": "GROUP_STAGE",
                "result": "home_win",
                "home_rank": 3,
                "away_rank": 1,
                "home_fifa_points": 1870.7,
                "away_fifa_points": 1877.3,
                "rank_difference": -2,
                "points_difference": -6.6,
            },
            {
                "home_team": "Brazil",
                "away_team": "Spain",
                "stage": "GROUP_STAGE",
                "result": "draw",
                "home_rank": 6,
                "away_rank": 2,
                "home_fifa_points": 1761.0,
                "away_fifa_points": 1874.7,
                "rank_difference": -4,
                "points_difference": -113.7,
            },
            {
                "home_team": "Germany",
                "away_team": "Italy",
                "stage": "GROUP_STAGE",
                "result": "away_win",
                "home_rank": 10,
                "away_rank": 9,
                "home_fifa_points": 1717.0,
                "away_fifa_points": 1718.0,
                "rank_difference": -1,
                "points_difference": -1.0,
            },
            {
                "home_team": "France",
                "away_team": "Brazil",
                "stage": "LAST_16",
                "result": "home_win",
                "home_rank": 3,
                "away_rank": 6,
                "home_fifa_points": 1870.7,
                "away_fifa_points": 1761.0,
                "rank_difference": 3,
                "points_difference": 109.7,
            },
        ]
    )
    model, _ = train_model(dataset)

    import joblib

    joblib.dump(model, model_path)

    loaded_model, model_uri = load_local_model(model_path)

    assert hasattr(loaded_model, "predict")
    assert model_uri == f"local:{model_path}"


def test_predict_match_returns_prediction_and_probabilities() -> None:
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

    result = predict_match(model, RANKINGS, "France", "Argentina", "GROUP_STAGE")

    assert result["prediction"] in {"home_win", "draw", "away_win"}
    assert abs(sum(result["probabilities"].values()) - 1) < 1e-6


def test_predict_match_is_neutral_to_team_order() -> None:
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
            row("Argentina", "France", "GROUP_STAGE", "away_win", 1, 3, 1877.3, 1870.7),
            row("Brazil", "Spain", "GROUP_STAGE", "draw", 6, 2, 1761.0, 1874.7),
            row("Spain", "Brazil", "GROUP_STAGE", "draw", 2, 6, 1874.7, 1761.0),
            row("Germany", "Italy", "GROUP_STAGE", "away_win", 10, 9, 1717.0, 1718.0),
            row("Italy", "Germany", "GROUP_STAGE", "home_win", 9, 10, 1718.0, 1717.0),
            row("France", "Brazil", "LAST_16", "home_win", 3, 6, 1870.7, 1761.0),
            row("Brazil", "France", "LAST_16", "away_win", 6, 3, 1761.0, 1870.7),
            row("Argentina", "Spain", "LAST_16", "draw", 1, 2, 1877.3, 1874.7),
            row("Spain", "Argentina", "LAST_16", "draw", 2, 1, 1874.7, 1877.3),
            row("Italy", "France", "QUARTER_FINALS", "away_win", 9, 3, 1718.0, 1870.7),
            row("France", "Italy", "QUARTER_FINALS", "home_win", 3, 9, 1870.7, 1718.0),
        ]
    )
    model, _ = train_model(dataset)

    france_vs_argentina = predict_match(model, RANKINGS, "France", "Argentina", "GROUP_STAGE")
    argentina_vs_france = predict_match(model, RANKINGS, "Argentina", "France", "GROUP_STAGE")

    assert france_vs_argentina["probabilities"]["home_win"] == pytest.approx(
        argentina_vs_france["probabilities"]["away_win"]
    )
    assert france_vs_argentina["probabilities"]["away_win"] == pytest.approx(
        argentina_vs_france["probabilities"]["home_win"]
    )
    assert france_vs_argentina["probabilities"]["draw"] == pytest.approx(
        argentina_vs_france["probabilities"]["draw"]
    )
