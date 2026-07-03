import sys

try:
    from scripts import (
        build_training_dataset,
        ingest_data,
        ingest_fifa_rankings,
        preprocess_fifa_rankings,
        preprocess_matches,
    )
except ImportError:
    import build_training_dataset
    import ingest_data
    import ingest_fifa_rankings
    import preprocess_fifa_rankings
    import preprocess_matches


def main() -> None:
    ingest_data.main()
    preprocess_matches.main()
    ingest_fifa_rankings.main()
    preprocess_fifa_rankings.main()
    build_training_dataset.main()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
