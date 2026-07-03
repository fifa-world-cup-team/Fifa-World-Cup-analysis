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
            "away_score": 0,
        },
        {
            "id": 3,
            "utc_date": "2026-07-01T06:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("Brazil"),
            "away_team": _team("Argentina"),
            "home_score": 1,
            "away_score": 0,
        },
        {
            "id": 4,
            "utc_date": "2026-07-01T09:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("Argentina"),
            "away_team": _team("Brazil"),
            "home_score": 1,
            "away_score": 0,
        },
        {
            "id": 5,
            "utc_date": "2026-07-01T12:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("Brazil"),
            "away_team": _team("Argentina"),
            "home_score": 1,
            "away_score": 0,
        },
        {
            "id": 6,
            "utc_date": "2026-07-01T15:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team("Spain"),
            "away_team": _team("Brazil"),
            "home_score": 1,
            "away_score": 0,
        },
        {
            "id": 7,
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


def test_simulate_knockout_stages_preserves_2026_bracket_halves(monkeypatch) -> None:
    def predict_home_win(model, rankings, home, away, stage):
        return {
            "prediction": "home_win",
            "probabilities": {"home_win": 0.8, "draw": 0.1, "away_win": 0.1},
        }

    monkeypatch.setattr("backend.tournament.predict_match", predict_home_win)

    round_of_32_winners = [
        "Germany",  # M74
        "Japan",  # M78
        "Paraguay",  # M73
        "Sweden",  # M75
        "Brazil",  # M76
        "France",  # M77
        "Mexico",  # M79
        "England",  # M80
        "Morocco",  # M83
        "Canada",  # M84
        "Spain",  # M81
        "Portugal",  # M82
        "Argentina",  # M86
        "Cabo Verde",  # M88
        "USA",  # M85
        "Belgium",  # M87
    ]
    matches = [
        {
            "id": index,
            "utc_date": f"2026-07-{index + 1:02d}T00:00:00Z",
            "status": "FINISHED",
            "stage": "LAST_32",
            "home_team": _team(winner),
            "away_team": _team(f"Loser {index}"),
            "home_score": 1,
            "away_score": 0,
        }
        for index, winner in enumerate(round_of_32_winners)
    ]

    for index in range(8):
        matches.append(
            {
                "id": 100 + index,
                "utc_date": f"2026-08-{index + 1:02d}T00:00:00Z",
                "status": "TIMED",
                "stage": "LAST_16",
                "home_team": None,
                "away_team": None,
                "home_score": None,
                "away_score": None,
            }
        )
    for index in range(4):
        matches.append(
            {
                "id": 200 + index,
                "utc_date": f"2026-09-{index + 1:02d}T00:00:00Z",
                "status": "TIMED",
                "stage": "QUARTER_FINALS",
                "home_team": None,
                "away_team": None,
                "home_score": None,
                "away_score": None,
            }
        )
    for index in range(2):
        matches.append(
            {
                "id": 300 + index,
                "utc_date": f"2026-10-{index + 1:02d}T00:00:00Z",
                "status": "TIMED",
                "stage": "SEMI_FINALS",
                "home_team": None,
                "away_team": None,
                "home_score": None,
                "away_score": None,
            }
        )
    matches.append(
        {
            "id": 400,
            "utc_date": "2026-11-01T00:00:00Z",
            "status": "TIMED",
            "stage": "FINAL",
            "home_team": None,
            "away_team": None,
            "home_score": None,
            "away_score": None,
        }
    )

    result = simulate_knockout_stages(None, RANKINGS, matches)

    last_16 = result["rounds"][1]["matches"]
    assert [(m["home_team"], m["away_team"]) for m in last_16] == [
        ("Germany", "France"),
        ("Paraguay", "Sweden"),
        ("Brazil", "Japan"),
        ("Mexico", "England"),
        ("Morocco", "Canada"),
        ("Spain", "Portugal"),
        ("Argentina", "Cabo Verde"),
        ("USA", "Belgium"),
    ]

    semi_finals = result["rounds"][3]["matches"]
    assert [(m["home_team"], m["away_team"]) for m in semi_finals] == [
        ("Germany", "Morocco"),
        ("Brazil", "Argentina"),
    ]
    assert {"Morocco", "Brazil"} not in [
        {match["home_team"], match["away_team"]} for match in semi_finals
    ]
