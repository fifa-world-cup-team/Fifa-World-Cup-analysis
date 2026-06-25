import csv
import json
import sys
from pathlib import Path
from typing import Any


RAW_PATH = Path("data/raw/worldcup_matches.json")
PROCESSED_PATH = Path("data/processed/matches_processed.csv")
FIELDNAMES = [
    "match_id",
    "date",
    "status",
    "stage",
    "group",
    "home_team",
    "away_team",
    "home_goals",
    "away_goals",
    "result",
]


def load_raw_matches(raw_path: Path = RAW_PATH) -> list[dict[str, Any]]:
    if not raw_path.exists():
        raise RuntimeError(
            f"Missing raw data file {raw_path}. Run scripts/ingest_data.py first."
        )

    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    matches = payload.get("matches")
    if not isinstance(matches, list):
        raise RuntimeError(f"Raw data file {raw_path} does not contain a matches list.")
    return matches


def get_result(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home_win"
    if home_goals < away_goals:
        return "away_win"
    return "draw"


def build_processed_rows(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []

    for match in matches:
        if match.get("status") != "FINISHED":
            continue

        full_time = match.get("score", {}).get("fullTime", {})
        home_goals = full_time.get("home")
        away_goals = full_time.get("away")
        if home_goals is None or away_goals is None:
            continue

        rows.append(
            {
                "match_id": match.get("id"),
                "date": match.get("utcDate"),
                "status": match.get("status"),
                "stage": match.get("stage"),
                "group": match.get("group") or "",
                "home_team": match.get("homeTeam", {}).get("name"),
                "away_team": match.get("awayTeam", {}).get("name"),
                "home_goals": home_goals,
                "away_goals": away_goals,
                "result": get_result(home_goals, away_goals),
            }
        )

    return rows


def save_processed_rows(
    rows: list[dict[str, Any]],
    processed_path: Path = PROCESSED_PATH,
) -> None:
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    with processed_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    matches = load_raw_matches()
    rows = build_processed_rows(matches)
    if not rows:
        raise RuntimeError("No finished matches with full-time scores were found.")

    save_processed_rows(rows)
    print(f"Processed {len(rows)} matches into {PROCESSED_PATH}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
