import sys
from pathlib import Path

import pandas as pd


MATCHES_PATH = Path("data/processed/matches_processed.csv")
RANKINGS_PATH = Path("data/processed/fifa_rankings_current.csv")
OUTPUT_PATH = Path("data/processed/training_matches.csv")
INITIAL_ELO = 1500.0
ELO_K_FACTOR = 30.0
RECENT_MATCH_COUNT = 5

TEAM_NAME_MAPPING = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cabo Verde",
    "Iran": "IR Iran",
    "Ivory Coast": "C\u00f4te d'Ivoire",
    "South Korea": "Korea Republic",
    "Turkey": "T\u00fcrkiye",
    "United States": "USA",
}

RANKING_COLUMNS = [
    "country",
    "confederation",
    "rank",
    "rank_change",
    "fifa_points",
    "points_change",
]

ENGINEERED_FEATURE_COLUMNS = [
    "home_elo",
    "away_elo",
    "elo_difference",
    "home_recent_form_points",
    "away_recent_form_points",
    "home_recent_goals_for_avg",
    "away_recent_goals_for_avg",
    "home_recent_goals_against_avg",
    "away_recent_goals_against_avg",
    "home_matches_played_before",
    "away_matches_played_before",
]


def normalize_team_name(team_name: str) -> str:
    return TEAM_NAME_MAPPING.get(team_name, team_name)


def load_csv(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise RuntimeError(f"Missing {label} file {path}.")
    return pd.read_csv(path)


def validate_columns(dataset: pd.DataFrame, required_columns: list[str], label: str) -> None:
    missing_columns = [
        column for column in required_columns if column not in dataset.columns
    ]
    if missing_columns:
        raise RuntimeError(
            f"{label} is missing required columns: " + ", ".join(missing_columns)
        )


def calculate_expected_score(team_elo: float, opponent_elo: float) -> float:
    return 1 / (1 + 10 ** ((opponent_elo - team_elo) / 400))


def result_to_scores(result: str) -> tuple[float, float]:
    if result == "home_win":
        return 1.0, 0.0
    if result == "away_win":
        return 0.0, 1.0
    return 0.5, 0.5


def team_match_points(result: str, side: str) -> float:
    home_score, away_score = result_to_scores(result)
    return home_score if side == "home" else away_score


def average_recent(values: list[float]) -> float:
    if not values:
        return 0.0
    recent_values = values[-RECENT_MATCH_COUNT:]
    return sum(recent_values) / len(recent_values)


def get_team_state(team: str, team_history: dict[str, dict[str, list[float] | float]]) -> dict:
    return team_history.setdefault(
        team,
        {
            "elo": INITIAL_ELO,
            "form_points": [],
            "goals_for": [],
            "goals_against": [],
        },
    )


def build_team_feature_values(
    team: str,
    team_history: dict[str, dict[str, list[float] | float]],
) -> dict[str, float]:
    state = get_team_state(team, team_history)
    form_points = state["form_points"]
    goals_for = state["goals_for"]
    goals_against = state["goals_against"]

    return {
        "elo": float(state["elo"]),
        "recent_form_points": average_recent(form_points),
        "recent_goals_for_avg": average_recent(goals_for),
        "recent_goals_against_avg": average_recent(goals_against),
        "matches_played_before": float(len(form_points)),
    }


def update_team_history(
    team_history: dict[str, dict[str, list[float] | float]],
    home_team: str,
    away_team: str,
    home_goals: int,
    away_goals: int,
    result: str,
) -> None:
    home_state = get_team_state(home_team, team_history)
    away_state = get_team_state(away_team, team_history)

    home_elo = float(home_state["elo"])
    away_elo = float(away_state["elo"])
    home_score, away_score = result_to_scores(result)
    expected_home = calculate_expected_score(home_elo, away_elo)
    expected_away = calculate_expected_score(away_elo, home_elo)

    home_state["elo"] = home_elo + ELO_K_FACTOR * (home_score - expected_home)
    away_state["elo"] = away_elo + ELO_K_FACTOR * (away_score - expected_away)

    home_state["form_points"].append(team_match_points(result, "home"))
    away_state["form_points"].append(team_match_points(result, "away"))
    home_state["goals_for"].append(float(home_goals))
    home_state["goals_against"].append(float(away_goals))
    away_state["goals_for"].append(float(away_goals))
    away_state["goals_against"].append(float(home_goals))


def add_engineered_match_features(matches: pd.DataFrame) -> pd.DataFrame:
    validate_columns(
        matches,
        [
            "date",
            "home_team",
            "away_team",
            "home_goals",
            "away_goals",
            "result",
        ],
        "matches dataset",
    )

    sort_columns = ["date"]
    if "match_id" in matches.columns:
        sort_columns.append("match_id")
    enriched = matches.copy().sort_values(sort_columns, na_position="last")
    team_history: dict[str, dict[str, list[float] | float]] = {}
    rows = []

    for _, match in enriched.iterrows():
        home_team = match["home_team"]
        away_team = match["away_team"]
        home_features = build_team_feature_values(home_team, team_history)
        away_features = build_team_feature_values(away_team, team_history)

        row = match.to_dict()
        row.update(
            {
                "home_elo": home_features["elo"],
                "away_elo": away_features["elo"],
                "elo_difference": home_features["elo"] - away_features["elo"],
                "home_recent_form_points": home_features["recent_form_points"],
                "away_recent_form_points": away_features["recent_form_points"],
                "home_recent_goals_for_avg": home_features["recent_goals_for_avg"],
                "away_recent_goals_for_avg": away_features["recent_goals_for_avg"],
                "home_recent_goals_against_avg": home_features[
                    "recent_goals_against_avg"
                ],
                "away_recent_goals_against_avg": away_features[
                    "recent_goals_against_avg"
                ],
                "home_matches_played_before": home_features["matches_played_before"],
                "away_matches_played_before": away_features["matches_played_before"],
            }
        )
        rows.append(row)

        update_team_history(
            team_history,
            home_team,
            away_team,
            int(match["home_goals"]),
            int(match["away_goals"]),
            match["result"],
        )

    return pd.DataFrame(rows)


def build_ranking_lookup(rankings: pd.DataFrame) -> pd.DataFrame:
    validate_columns(rankings, RANKING_COLUMNS, "FIFA rankings dataset")
    return rankings[RANKING_COLUMNS].drop_duplicates(subset=["country"])


def add_team_ranking_features(
    matches: pd.DataFrame,
    rankings: pd.DataFrame,
    side: str,
) -> pd.DataFrame:
    team_column = f"{side}_team"
    mapped_column = f"{side}_ranking_country"
    prefix = f"{side}_"

    enriched = matches.copy()
    enriched[mapped_column] = enriched[team_column].map(normalize_team_name)

    ranking_features = rankings.rename(
        columns={
            "country": mapped_column,
            "confederation": f"{prefix}confederation",
            "rank": f"{prefix}rank",
            "rank_change": f"{prefix}rank_change",
            "fifa_points": f"{prefix}fifa_points",
            "points_change": f"{prefix}points_change",
        }
    )

    return enriched.merge(ranking_features, on=mapped_column, how="left")


def find_missing_rankings(training_dataset: pd.DataFrame) -> list[str]:
    missing_home = training_dataset.loc[
        training_dataset["home_rank"].isna(), "home_team"
    ].tolist()
    missing_away = training_dataset.loc[
        training_dataset["away_rank"].isna(), "away_team"
    ].tolist()
    return sorted(set(missing_home + missing_away))


def build_training_dataset(matches: pd.DataFrame, rankings: pd.DataFrame) -> pd.DataFrame:
    validate_columns(
        matches,
        ["home_team", "away_team", "stage", "result"],
        "matches dataset",
    )

    ranking_lookup = build_ranking_lookup(rankings)
    matches_with_history = add_engineered_match_features(matches)
    training_dataset = add_team_ranking_features(matches_with_history, ranking_lookup, "home")
    training_dataset = add_team_ranking_features(training_dataset, ranking_lookup, "away")

    missing_rankings = find_missing_rankings(training_dataset)
    if missing_rankings:
        raise RuntimeError(
            "Missing FIFA ranking for teams: " + ", ".join(missing_rankings)
        )

    training_dataset["rank_difference"] = (
        training_dataset["away_rank"] - training_dataset["home_rank"]
    )
    training_dataset["points_difference"] = (
        training_dataset["home_fifa_points"] - training_dataset["away_fifa_points"]
    )

    return training_dataset


def save_training_dataset(
    training_dataset: pd.DataFrame,
    output_path: Path = OUTPUT_PATH,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    training_dataset.to_csv(output_path, index=False)


def main() -> None:
    matches = load_csv(MATCHES_PATH, "matches")
    rankings = load_csv(RANKINGS_PATH, "FIFA rankings")
    training_dataset = build_training_dataset(matches, rankings)
    save_training_dataset(training_dataset)
    print(f"Built {len(training_dataset)} training rows into {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
