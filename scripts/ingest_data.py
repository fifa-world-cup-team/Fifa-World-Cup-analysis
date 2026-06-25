import json
import os
import sys
from pathlib import Path

import requests


DEFAULT_BASE_URL = "https://api.football-data.org/v4"
DEFAULT_COMPETITION = "WC"
OUTPUT_PATH = Path("data/raw/worldcup_matches.json")
ENV_PATH = Path(".env")


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        name, value = clean_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable {name}. "
            "Set it before running the ingestion script."
        )
    return value


def build_matches_url(base_url: str, competition: str) -> str:
    clean_base_url = base_url.rstrip("/")
    return f"{clean_base_url}/competitions/{competition}/matches"


def fetch_matches(api_key: str, base_url: str, competition: str) -> dict:
    url = build_matches_url(base_url, competition)
    response = requests.get(
        url,
        headers={"X-Auth-Token": api_key},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def save_raw_payload(payload: dict, output_path: Path = OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    load_env_file()
    api_key = get_required_env("FOOTBALL_DATA_API_KEY")
    base_url = os.getenv("FOOTBALL_DATA_BASE_URL", DEFAULT_BASE_URL)
    competition = os.getenv("FOOTBALL_DATA_COMPETITION", DEFAULT_COMPETITION)

    payload = fetch_matches(api_key, base_url, competition)
    save_raw_payload(payload)
    print(f"Raw match data saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
