from pathlib import Path

import pandas as pd

from scripts.train_baseline_model import get_dvc_data_version, train_model


def test_train_model_returns_model_and_accuracy() -> None:
    def row(
        home_team: str,
        away_team: str,
        stage: str,
        result: str,
        home_rank: int,
        away_rank: int,
        home_points: float,
        away_points: float,
    ) -> dict[str, object]:
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
            row("Spain", "Germany", "ROUND_OF_16", "draw", 2, 10, 1874.7, 1717.0),
            row("Italy", "Argentina", "ROUND_OF_16", "away_win", 9, 1, 1718.0, 1877.3),
            row("Argentina", "Brazil", "QUARTER_FINALS", "home_win", 1, 6, 1877.3, 1761.0),
            row("Germany", "France", "QUARTER_FINALS", "draw", 10, 3, 1717.0, 1870.7),
            row("Spain", "Italy", "QUARTER_FINALS", "away_win", 2, 9, 1874.7, 1718.0),
            row("Brazil", "Germany", "SEMI_FINALS", "home_win", 6, 10, 1761.0, 1717.0),
            row("Italy", "France", "SEMI_FINALS", "draw", 9, 3, 1718.0, 1870.7),
            row("Argentina", "Spain", "SEMI_FINALS", "away_win", 1, 2, 1877.3, 1874.7),
        ]
    )

    model, accuracy = train_model(dataset)

    assert hasattr(model, "predict")
    assert 0 <= accuracy <= 1


def test_get_dvc_data_version_reads_md5_from_pointer_file(tmp_path: Path) -> None:
    dvc_pointer = tmp_path / "training_matches.csv.dvc"
    dvc_pointer.write_text(
        "outs:\n- md5: c2845b97dbdd731141764def7ab8fec2\n  size: 15540\n",
        encoding="utf-8",
    )

    assert get_dvc_data_version(dvc_pointer) == "c2845b97dbdd731141764def7ab8fec2"


def test_get_dvc_data_version_returns_unknown_when_pointer_missing(
    tmp_path: Path,
) -> None:
    assert get_dvc_data_version(tmp_path / "missing.dvc") == "unknown"
