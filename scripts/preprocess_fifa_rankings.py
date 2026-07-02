import csv
import json
import sys
from pathlib import Path
from typing import Any


RAW_PATH = Path("data/raw/fifa_ranking_current.json")
PROCESSED_PATH = Path("data/processed/fifa_rankings_current.csv")
FIELDNAMES = [
    "ranking_date",
    "ranking_type",
    "country",
    "confederation",
    "rank",
    "previous_rank",
    "rank_change",
    "fifa_points",
    "previous_points",
    "points_change",
]


def load_raw_ranking(raw_path: Path = RAW_PATH) -> dict[str, Any]:
    if not raw_path.exists():
        raise RuntimeError(
            f"Missing FIFA ranking file {raw_path}. "
            "Run scripts/ingest_fifa_rankings.py first."
        )

    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    ranking = payload.get("ranking")
    if not isinstance(ranking, list):
        raise RuntimeError(f"Raw ranking file {raw_path} does not contain a ranking list.")
    return payload


def calculate_difference(current: float | int | None, previous: float | int | None) -> float | int | str:
    if current is None or previous is None:
        return ""
    return current - previous


def build_ranking_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    ranking_date = payload.get("date", "")
    ranking_type = payload.get("type", "")
    rows = []

    for team in payload.get("ranking", []):
        rank = team.get("rank")
        previous_rank = team.get("previous_rank")
        fifa_points = team.get("points")
        previous_points = team.get("previous_points")

        rows.append(
            {
                "ranking_date": ranking_date,
                "ranking_type": ranking_type,
                "country": team.get("name"),
                "confederation": team.get("confederation"),
                "rank": rank,
                "previous_rank": previous_rank,
                "rank_change": calculate_difference(previous_rank, rank),
                "fifa_points": fifa_points,
                "previous_points": previous_points,
                "points_change": calculate_difference(fifa_points, previous_points),
            }
        )

    return rows


def save_ranking_rows(
    rows: list[dict[str, Any]],
    processed_path: Path = PROCESSED_PATH,
) -> None:
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    with processed_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    payload = load_raw_ranking()
    rows = build_ranking_rows(payload)
    if not rows:
        raise RuntimeError("No FIFA ranking rows were found.")

    save_ranking_rows(rows)
    print(f"Processed {len(rows)} FIFA ranking rows into {PROCESSED_PATH}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
