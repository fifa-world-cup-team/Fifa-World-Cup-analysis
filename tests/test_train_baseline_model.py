import pandas as pd

from scripts.train_baseline_model import train_model


def test_train_model_returns_model_and_accuracy() -> None:
    dataset = pd.DataFrame(
        [
            {"home_team": "France", "away_team": "Argentina", "stage": "GROUP_STAGE", "result": "home_win"},
            {"home_team": "Brazil", "away_team": "Spain", "stage": "GROUP_STAGE", "result": "draw"},
            {"home_team": "Germany", "away_team": "Italy", "stage": "GROUP_STAGE", "result": "away_win"},
            {"home_team": "France", "away_team": "Brazil", "stage": "ROUND_OF_16", "result": "home_win"},
            {"home_team": "Spain", "away_team": "Germany", "stage": "ROUND_OF_16", "result": "draw"},
            {"home_team": "Italy", "away_team": "Argentina", "stage": "ROUND_OF_16", "result": "away_win"},
            {"home_team": "Argentina", "away_team": "Brazil", "stage": "QUARTER_FINALS", "result": "home_win"},
            {"home_team": "Germany", "away_team": "France", "stage": "QUARTER_FINALS", "result": "draw"},
            {"home_team": "Spain", "away_team": "Italy", "stage": "QUARTER_FINALS", "result": "away_win"},
            {"home_team": "Brazil", "away_team": "Germany", "stage": "SEMI_FINALS", "result": "home_win"},
            {"home_team": "Italy", "away_team": "France", "stage": "SEMI_FINALS", "result": "draw"},
            {"home_team": "Argentina", "away_team": "Spain", "stage": "SEMI_FINALS", "result": "away_win"},
        ]
    )

    model, accuracy = train_model(dataset)

    assert hasattr(model, "predict")
    assert 0 <= accuracy <= 1
