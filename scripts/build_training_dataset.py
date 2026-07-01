import sys
from pathlib import Path

import pandas as pd


MATCHES_PATH = Path("data/processed/matches_processed.csv")
RANKINGS_PATH = Path("data/processed/fifa_rankings_current.csv")
OUTPUT_PATH = Path("data/processed/training_matches.csv")

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
    training_dataset = add_team_ranking_features(matches, ranking_lookup, "home")
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
