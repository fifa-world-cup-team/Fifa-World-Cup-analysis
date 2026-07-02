from pathlib import Path

import pandas as pd

from scripts.build_training_dataset import (
    build_training_dataset,
    load_csv,
    save_training_dataset,
)

MATCHES_FIXTURE = Path("tests/fixtures/matches_processed_sample.csv")
RANKINGS_FIXTURE = Path("tests/fixtures/rankings_sample.csv")


def test_build_training_dataset_merges_real_csv_files_on_disk(tmp_path: Path) -> None:
    output_path = tmp_path / "training_matches.csv"

    matches = load_csv(MATCHES_FIXTURE, "matches")
    rankings = load_csv(RANKINGS_FIXTURE, "FIFA rankings")

    training_dataset = build_training_dataset(matches, rankings)
    save_training_dataset(training_dataset, output_path)

    saved_dataset = pd.read_csv(output_path)

    assert len(saved_dataset) == len(matches)
    assert {"home_rank", "away_rank", "rank_difference", "points_difference"}.issubset(
        saved_dataset.columns
    )
    assert saved_dataset["home_rank"].notna().all()
    assert saved_dataset["away_rank"].notna().all()
