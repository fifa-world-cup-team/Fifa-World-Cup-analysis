from scripts.preprocess_matches import build_processed_rows, get_result


def test_get_result_home_win() -> None:
    assert get_result(2, 1) == "home_win"


def test_get_result_draw() -> None:
    assert get_result(1, 1) == "draw"


def test_get_result_away_win() -> None:
    assert get_result(0, 3) == "away_win"


def test_build_processed_rows_ignores_unfinished_matches() -> None:
    matches = [
        {
            "id": 1,
            "utcDate": "2026-06-11T19:00:00Z",
            "status": "FINISHED",
            "stage": "GROUP_STAGE",
            "group": "GROUP_A",
            "homeTeam": {"name": "France"},
            "awayTeam": {"name": "Argentina"},
            "score": {"fullTime": {"home": 2, "away": 1}},
        },
        {
            "id": 2,
            "utcDate": "2026-06-12T19:00:00Z",
            "status": "SCHEDULED",
            "stage": "GROUP_STAGE",
            "group": "GROUP_A",
            "homeTeam": {"name": "Brazil"},
            "awayTeam": {"name": "Spain"},
            "score": {"fullTime": {"home": None, "away": None}},
        },
    ]

    rows = build_processed_rows(matches)

    assert len(rows) == 1
    assert rows[0]["match_id"] == 1
    assert rows[0]["result"] == "home_win"
