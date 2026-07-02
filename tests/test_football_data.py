from backend.football_data import cached_get, simplify_match, simplify_standings


def test_simplify_match_extracts_expected_fields() -> None:
    raw_match = {
        "id": 1,
        "utcDate": "2026-06-11T19:00:00Z",
        "status": "FINISHED",
        "stage": "GROUP_STAGE",
        "group": "GROUP_A",
        "matchday": 1,
        "homeTeam": {"name": "France", "crest": "https://example.com/fra.svg"},
        "awayTeam": {"name": "Argentina", "crest": "https://example.com/arg.svg"},
        "score": {"fullTime": {"home": 2, "away": 1}},
    }

    row = simplify_match(raw_match)

    assert row["home_team"] == {"name": "France", "crest": "https://example.com/fra.svg"}
    assert row["away_team"] == {"name": "Argentina", "crest": "https://example.com/arg.svg"}
    assert row["home_score"] == 2
    assert row["away_score"] == 1
    assert row["stage"] == "GROUP_STAGE"


def test_simplify_match_handles_unknown_teams() -> None:
    raw_match = {
        "id": 2,
        "utcDate": "2026-07-06T19:00:00Z",
        "status": "TIMED",
        "stage": "LAST_16",
        "group": None,
        "matchday": None,
        "homeTeam": None,
        "awayTeam": None,
        "score": {"fullTime": {"home": None, "away": None}},
    }

    row = simplify_match(raw_match)

    assert row["home_team"] is None
    assert row["away_team"] is None
    assert row["home_score"] is None


def test_simplify_standings_extracts_group_tables() -> None:
    payload = {
        "standings": [
            {
                "group": "Group A",
                "table": [
                    {
                        "position": 1,
                        "team": {"name": "Mexico", "crest": "https://example.com/mex.svg"},
                        "playedGames": 3,
                        "won": 3,
                        "draw": 0,
                        "lost": 0,
                        "points": 9,
                        "goalDifference": 6,
                    }
                ],
            }
        ]
    }

    groups = simplify_standings(payload)

    assert groups == [
        {
            "group": "Group A",
            "table": [
                {
                    "position": 1,
                    "team": "Mexico",
                    "crest": "https://example.com/mex.svg",
                    "played": 3,
                    "won": 3,
                    "draw": 0,
                    "lost": 0,
                    "points": 9,
                    "goal_difference": 6,
                }
            ],
        }
    ]


def test_cached_get_reuses_cached_value_within_ttl() -> None:
    cache: dict = {"matches": {"data": {"cached": True}, "fetched_at": 10**12}}

    result = cached_get("matches", "https://unused.example.com", cache=cache)

    assert result == {"cached": True}
