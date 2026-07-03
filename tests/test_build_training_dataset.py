import pandas as pd

from scripts.build_training_dataset import build_training_dataset, normalize_team_name


def _rankings() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "country": "France",
                "confederation": "UEFA",
                "rank": 3,
                "rank_change": -2,
                "fifa_points": 1870.7,
                "points_change": -6.6,
            },
            {
                "country": "Argentina",
                "confederation": "CONMEBOL",
                "rank": 1,
                "rank_change": 2,
                "fifa_points": 1877.3,
                "points_change": 2.5,
            },
            {
                "country": "Brazil",
                "confederation": "CONMEBOL",
                "rank": 6,
                "rank_change": 0,
                "fifa_points": 1761.0,
                "points_change": 1.0,
            },
            {
                "country": "Spain",
                "confederation": "UEFA",
                "rank": 2,
                "rank_change": 0,
                "fifa_points": 1874.7,
                "points_change": -1.0,
            },
        ]
    )


def test_normalize_team_name_maps_source_differences() -> None:
    assert normalize_team_name("South Korea") == "Korea Republic"
    assert normalize_team_name("United States") == "USA"
    assert normalize_team_name("France") == "France"


def test_build_training_dataset_adds_ranking_features() -> None:
    matches = pd.DataFrame(
        [
            {
                "match_id": 1,
                "date": "2026-06-11T19:00:00Z",
                "stage": "GROUP_STAGE",
                "home_team": "France",
                "away_team": "Argentina",
                "home_goals": 2,
                "away_goals": 1,
                "result": "home_win",
            }
        ]
    )
    rankings = _rankings()

    training_dataset = build_training_dataset(matches, rankings)
    row = training_dataset.iloc[0]

    assert row["home_rank"] == 3
    assert row["away_rank"] == 1
    assert row["home_fifa_points"] == 1870.7
    assert row["away_fifa_points"] == 1877.3
    assert row["home_confederation"] == "UEFA"
    assert row["away_confederation"] == "CONMEBOL"
    assert row["rank_difference"] == -2
    assert round(row["points_difference"], 1) == -6.6
    assert row["home_elo"] == 1500.0
    assert row["away_elo"] == 1500.0
    assert row["elo_difference"] == 0.0


def test_build_training_dataset_uses_name_mapping_for_join() -> None:
    matches = pd.DataFrame(
        [
            {
                "date": "2026-06-11T19:00:00Z",
                "home_team": "South Korea",
                "away_team": "United States",
                "stage": "GROUP_STAGE",
                "home_goals": 1,
                "away_goals": 1,
                "result": "draw",
            }
        ]
    )
    rankings = pd.DataFrame(
        [
            {
                "country": "Korea Republic",
                "confederation": "AFC",
                "rank": 25,
                "rank_change": 1,
                "fifa_points": 1585.0,
                "points_change": 3.0,
            },
            {
                "country": "USA",
                "confederation": "CONCACAF",
                "rank": 17,
                "rank_change": 0,
                "fifa_points": 1634.0,
                "points_change": 1.0,
            },
        ]
    )

    training_dataset = build_training_dataset(matches, rankings)
    row = training_dataset.iloc[0]

    assert row["home_ranking_country"] == "Korea Republic"
    assert row["away_ranking_country"] == "USA"
    assert row["rank_difference"] == -8


def test_engineered_features_do_not_use_current_match_result() -> None:
    matches = pd.DataFrame(
        [
            {
                "match_id": 1,
                "date": "2026-06-11T19:00:00Z",
                "stage": "GROUP_STAGE",
                "home_team": "France",
                "away_team": "Argentina",
                "home_goals": 3,
                "away_goals": 0,
                "result": "home_win",
            }
        ]
    )

    training_dataset = build_training_dataset(matches, _rankings())
    row = training_dataset.iloc[0]

    assert row["home_recent_form_points"] == 0.0
    assert row["away_recent_form_points"] == 0.0
    assert row["home_recent_goals_for_avg"] == 0.0
    assert row["away_recent_goals_against_avg"] == 0.0
    assert row["home_matches_played_before"] == 0.0
    assert row["away_matches_played_before"] == 0.0


def test_engineered_features_follow_team_across_home_and_away_matches() -> None:
    matches = pd.DataFrame(
        [
            {
                "match_id": 1,
                "date": "2026-06-11T19:00:00Z",
                "stage": "GROUP_STAGE",
                "home_team": "France",
                "away_team": "Argentina",
                "home_goals": 3,
                "away_goals": 1,
                "result": "home_win",
            },
            {
                "match_id": 2,
                "date": "2026-06-12T19:00:00Z",
                "stage": "GROUP_STAGE",
                "home_team": "Brazil",
                "away_team": "France",
                "home_goals": 2,
                "away_goals": 2,
                "result": "draw",
            },
        ]
    )

    training_dataset = build_training_dataset(matches, _rankings())
    france_second_match = training_dataset.iloc[1]

    assert france_second_match["away_matches_played_before"] == 1.0
    assert france_second_match["away_recent_form_points"] == 1.0
    assert france_second_match["away_recent_goals_for_avg"] == 3.0
    assert france_second_match["away_recent_goals_against_avg"] == 1.0
    assert france_second_match["away_elo"] > 1500.0
