import pandas as pd

from backend.tournament import simulate_knockout_stages
from scripts.train_baseline_model import train_model

RANKINGS = pd.DataFrame(
    [
        {"country": "France", "confederation": "UEFA", "rank": 3, "fifa_points": 1870.7},
        {"country": "Argentina", "confederation": "CONMEBOL", "rank": 1, "fifa_points": 1877.3},
        {"country": "Brazil", "confederation": "CONMEBOL", "rank": 6, "fifa_points": 1761.0},
        {"country": "Spain", "confederation": "UEFA", "rank": 2, "fifa_points": 1874.7},
    ]
)


def _team(name):
    return {"name": name, "crest": None}


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
            row("France", "Brazil", "LAST_16", "home_win", 3, 6, 1870.7, 1761.0),
            row("Argentina", "Spain", "LAST_16", "away_win", 1, 2, 1877.3, 1874.7),
        ]
    )
    model, _ = train_model(dataset)
    return model


def test_simulate_knockout_stages_fills_unresolved_slot_from_finished_winners() -> None:
    model = _train_stub_model()

    matches = [
        {
            "id": 1,
            "utc_date": "2026-07-01T00:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("France"),
            "away_team": _team("Brazil"),
            "home_score": 2,
            "away_score": 0,
        },
        {
            "id": 2,
            "utc_date": "2026-07-01T03:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("Argentina"),
            "away_team": _team("Spain"),
            "home_score": 1,
            "away_score": 3,
        },
        {
            "id": 3,
            "utc_date": "2026-07-04T00:00:00Z",
            "status": "TIMED",
            "stage": "LAST_16",
            "home_team": None,
            "away_team": None,
            "home_score": None,
            "away_score": None,
        },
    ]

    result = simulate_knockout_stages(model, RANKINGS, matches)

    last_16_match = result["rounds"][1]["matches"][0]
    assert last_16_match["resolved"] is True
    assert {last_16_match["home_team"], last_16_match["away_team"]} == {"France", "Spain"}
    assert result["champion"] is None  # no FINAL stage in this synthetic bracket


def test_simulate_knockout_stages_does_not_reuse_a_team_already_in_a_known_fixture() -> None:
    model = _train_stub_model()

    matches = [
        {
            "id": 1,
            "utc_date": "2026-07-01T00:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("France"),
            "away_team": _team("Brazil"),
            "home_score": 2,
            "away_score": 0,
        },
        {
            "id": 2,
            "utc_date": "2026-07-01T03:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("Argentina"),
            "away_team": _team("Spain"),
            "home_score": 1,
            "away_score": 3,
        },
        {
            # Already-known fixture: France (a LAST_32 winner) is directly assigned here.
            "id": 3,
            "utc_date": "2026-07-04T00:00:00Z",
            "status": "TIMED",
            "stage": "LAST_16",
            "home_team": _team("France"),
            "away_team": None,
            "home_score": None,
            "away_score": None,
        },
        {
            # Fully unresolved slot: must NOT be filled with "France" again.
            "id": 4,
            "utc_date": "2026-07-04T03:00:00Z",
            "status": "TIMED",
            "stage": "LAST_16",
            "home_team": None,
            "away_team": None,
            "home_score": None,
            "away_score": None,
        },
    ]

    result = simulate_knockout_stages(model, RANKINGS, matches)
    last_16 = result["rounds"][1]["matches"]

    teams_seen = [m["home_team"] for m in last_16] + [m["away_team"] for m in last_16]
    teams_seen = [t for t in teams_seen if t is not None]
    assert len(teams_seen) == len(set(teams_seen)), f"a team was reused: {teams_seen}"
