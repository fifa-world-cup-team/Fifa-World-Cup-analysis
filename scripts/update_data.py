import sys

import ingest_data
import preprocess_matches


def main() -> None:
    ingest_data.main()
    preprocess_matches.main()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
