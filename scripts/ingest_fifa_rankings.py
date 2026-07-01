import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

import requests


DEFAULT_BASE_URL = "https://world-football-ranking.p.rapidapi.com"
DEFAULT_HOST = "world-football-ranking.p.rapidapi.com"
DEFAULT_RANKING_TYPE = "official"
OUTPUT_PATH = Path("data/raw/fifa_ranking_current.json")
ENV_PATH = Path(".env")
API_KEY_ENV_NAMES = (
    "WORLD_FOOTBALL_RANKING_API_KEY",
    "X_RAPIDAPI_KEY",
    "RAPIDAPI_KEY",
)


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        name, value = clean_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def get_required_api_key() -> str:
    for name in API_KEY_ENV_NAMES:
        value = os.getenv(name)
        if value:
            return value

    raise RuntimeError(
        "Missing RapidAPI key. Set WORLD_FOOTBALL_RANKING_API_KEY in your .env file."
    )


def build_current_ranking_url(base_url: str, ranking_type: str) -> str:
    clean_base_url = base_url.rstrip("/")
    query = urlencode({"type": ranking_type})
    return f"{clean_base_url}/current-ranking.php?{query}"


def fetch_current_ranking(
    api_key: str,
    base_url: str,
    host: str,
    ranking_type: str,
) -> dict:
    url = build_current_ranking_url(base_url, ranking_type)
    response = requests.get(
        url,
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": host,
        },
        timeout=30,
    )
    if response.status_code in {401, 403}:
        raise RuntimeError(
            "RapidAPI refused the request. Check that your API key is valid and "
            "that the World Football Ranking API is enabled on your RapidAPI account."
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
    api_key = get_required_api_key()
    base_url = os.getenv("WORLD_FOOTBALL_RANKING_BASE_URL", DEFAULT_BASE_URL)
    host = os.getenv("WORLD_FOOTBALL_RANKING_HOST", DEFAULT_HOST)
    ranking_type = os.getenv("WORLD_FOOTBALL_RANKING_TYPE", DEFAULT_RANKING_TYPE)

    payload = fetch_current_ranking(api_key, base_url, host, ranking_type)
    save_raw_payload(payload)
    print(f"FIFA ranking data saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, requests.RequestException) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
