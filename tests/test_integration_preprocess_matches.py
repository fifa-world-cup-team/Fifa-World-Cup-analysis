import csv
from pathlib import Path

from scripts.preprocess_matches import (
    build_processed_rows,
    load_raw_matches,
    save_processed_rows,
)

FIXTURE_PATH = Path("tests/fixtures/raw_matches_sample.json")


def test_preprocess_pipeline_round_trips_through_disk(tmp_path: Path) -> None:
    output_path = tmp_path / "matches_processed.csv"

    matches = load_raw_matches(FIXTURE_PATH)
    rows = build_processed_rows(matches)
    save_processed_rows(rows, output_path)

    with output_path.open(encoding="utf-8") as csv_file:
        saved_rows = list(csv.DictReader(csv_file))

    # 5 FINISHED matches in the fixture, 1 SCHEDULED match filtered out.
    assert len(saved_rows) == 5
    assert {row["result"] for row in saved_rows} == {"home_win", "draw", "away_win"}

    france_vs_argentina = next(
        row for row in saved_rows if row["match_id"] == "101"
    )
    assert france_vs_argentina["home_team"] == "France"
    assert france_vs_argentina["away_team"] == "Argentina"
    assert france_vs_argentina["result"] == "home_win"
