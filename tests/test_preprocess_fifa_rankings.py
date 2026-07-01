from scripts.preprocess_fifa_rankings import (
    build_ranking_rows,
    calculate_difference,
)


def test_calculate_difference_returns_empty_value_for_missing_values() -> None:
    assert calculate_difference(None, 10) == ""
    assert calculate_difference(10, None) == ""


def test_build_ranking_rows_creates_ml_ready_features() -> None:
    payload = {
        "type": "Official",
        "date": "11 June, 2026",
        "ranking": [
            {
                "rank": 1,
                "name": "Argentina",
                "points": 1877.27,
                "previous_rank": 3,
                "previous_points": 1874.81,
                "confederation": "CONMEBOL",
            }
        ],
    }

    rows = build_ranking_rows(payload)

    assert rows == [
        {
            "ranking_date": "11 June, 2026",
            "ranking_type": "Official",
            "country": "Argentina",
            "confederation": "CONMEBOL",
            "rank": 1,
            "previous_rank": 3,
            "rank_change": 2,
            "fifa_points": 1877.27,
            "previous_points": 1874.81,
            "points_change": 2.4600000000000364,
        }
    ]
