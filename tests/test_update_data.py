from scripts import update_data


def test_update_data_runs_full_data_pipeline(monkeypatch) -> None:
    calls = []

    monkeypatch.setattr(update_data.ingest_data, "main", lambda: calls.append("ingest_matches"))
    monkeypatch.setattr(
        update_data.preprocess_matches,
        "main",
        lambda: calls.append("preprocess_matches"),
    )
    monkeypatch.setattr(
        update_data.ingest_fifa_rankings,
        "main",
        lambda: calls.append("ingest_fifa_rankings"),
    )
    monkeypatch.setattr(
        update_data.preprocess_fifa_rankings,
        "main",
        lambda: calls.append("preprocess_fifa_rankings"),
    )
    monkeypatch.setattr(
        update_data.build_training_dataset,
        "main",
        lambda: calls.append("build_training_dataset"),
    )

    update_data.main()

    assert calls == [
        "ingest_matches",
        "preprocess_matches",
        "ingest_fifa_rankings",
        "preprocess_fifa_rankings",
        "build_training_dataset",
    ]
