import os
import time
from pathlib import Path

import requests

ENV_PATH = Path(".env")
BASE_URL_DEFAULT = "https://api.football-data.org/v4"
COMPETITION_DEFAULT = "WC"
CACHE_TTL_SECONDS = 60

_cache: dict = {}


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        name, value = clean_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def get_api_key() -> str:
    load_env_file()
    key = os.getenv("FOOTBALL_DATA_API_KEY")
    if not key:
        raise RuntimeError("Missing FOOTBALL_DATA_API_KEY.")
    return key


def get_base_url() -> str:
    return os.getenv("FOOTBALL_DATA_BASE_URL", BASE_URL_DEFAULT).rstrip("/")


def get_competition() -> str:
    return os.getenv("FOOTBALL_DATA_COMPETITION", COMPETITION_DEFAULT)


def cached_get(cache_key: str, url: str, cache: dict = _cache) -> dict:
    now = time.time()
    cached = cache.get(cache_key)
    if cached and now - cached["fetched_at"] < CACHE_TTL_SECONDS:
        return cached["data"]

    api_key = get_api_key()
    response = requests.get(url, headers={"X-Auth-Token": api_key}, timeout=15)
    response.raise_for_status()
    data = response.json()
    cache[cache_key] = {"data": data, "fetched_at": now}
    return data


def simplify_team(team: dict | None) -> dict | None:
    if team is None:
        return None
    return {"name": team.get("name"), "crest": team.get("crest")}


def simplify_match(match: dict) -> dict:
    full_time = match.get("score", {}).get("fullTime", {})
    return {
        "id": match["id"],
        "utc_date": match["utcDate"],
        "status": match["status"],
        "stage": match["stage"],
        "group": match.get("group"),
        "matchday": match.get("matchday"),
        "home_team": simplify_team(match.get("homeTeam")),
        "away_team": simplify_team(match.get("awayTeam")),
        "home_score": full_time.get("home"),
        "away_score": full_time.get("away"),
    }


def get_matches() -> list[dict]:
    url = f"{get_base_url()}/competitions/{get_competition()}/matches"
    data = cached_get("matches", url)
    return [simplify_match(match) for match in data.get("matches", [])]


def simplify_standings(payload: dict) -> list[dict]:
    groups = []
    for entry in payload.get("standings", []):
        groups.append(
            {
                "group": entry.get("group"),
                "table": [
                    {
                        "position": row["position"],
                        "team": row["team"]["name"],
                        "crest": row["team"].get("crest"),
                        "played": row["playedGames"],
                        "won": row["won"],
                        "draw": row["draw"],
                        "lost": row["lost"],
                        "points": row["points"],
                        "goal_difference": row["goalDifference"],
                    }
                    for row in entry.get("table", [])
                ],
            }
        )
    return groups


def get_standings() -> list[dict]:
    url = f"{get_base_url()}/competitions/{get_competition()}/standings"
    data = cached_get("standings", url)
    return simplify_standings(data)
