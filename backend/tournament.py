from backend.model_service import PredictionError, predict_match

KNOCKOUT_STAGES = [
    "LAST_32",
    "LAST_16",
    "QUARTER_FINALS",
    "SEMI_FINALS",
    "THIRD_PLACE",
    "FINAL",
]

# Match numbers are assigned from the chronological football-data.org order.
# The 2026 bracket is not a simple chronological chain: some round-of-32
# winners feed different quarters and semi-finals. Keeping these feeds avoids
# impossible fixtures between teams that are on opposite sides of the bracket.
STAGE_MATCH_NUMBERS_BY_DATE = {
    "LAST_32": [74, 77, 73, 75, 76, 78, 79, 80, 83, 84, 81, 82, 86, 88, 85, 87],
    "LAST_16": [89, 90, 91, 92, 93, 94, 95, 96],
    "QUARTER_FINALS": [97, 98, 99, 100],
    "SEMI_FINALS": [101, 102],
    "THIRD_PLACE": [103],
    "FINAL": [104],
}

WINNER_FEEDS = {
    89: (74, 77),
    90: (73, 75),
    91: (76, 78),
    92: (79, 80),
    93: (83, 84),
    94: (81, 82),
    95: (86, 88),
    96: (85, 87),
    97: (89, 90),
    98: (93, 94),
    99: (91, 92),
    100: (95, 96),
    101: (97, 98),
    102: (99, 100),
    104: (101, 102),
}

LOSER_FEEDS = {
    103: (101, 102),
}


def _team_name(team: dict | None) -> str | None:
    return team["name"] if team else None


def _decide_winner_loser(match: dict, home: str, away: str) -> tuple[str, str]:
    if match["home_score"] is not None and match["home_score"] > match["away_score"]:
        return home, away
    if match["away_score"] is not None and match["away_score"] > match["home_score"]:
        return away, home
    return home, away


def _match_numbers_for_stage(stage: str, stage_matches: list[dict]) -> list[int]:
    configured = STAGE_MATCH_NUMBERS_BY_DATE.get(stage, [])
    if len(configured) >= len(stage_matches):
        return configured[: len(stage_matches)]

    fallback_start = configured[-1] + 1 if configured else 1
    missing_count = len(stage_matches) - len(configured)
    return configured + list(range(fallback_start, fallback_start + missing_count))


def _fill_missing_teams(
    home: str | None,
    away: str | None,
    feed: tuple[str | None, str | None],
) -> tuple[str | None, str | None]:
    candidates = [team for team in feed if team]

    if home is None:
        home = next((team for team in candidates if team != away), None)
        if home:
            candidates.remove(home)

    if away is None:
        away = next((team for team in candidates if team != home), None)

    return home, away


def _unresolved_result(match_number: int, home: str | None, away: str | None) -> dict:
    return {
        "match_number": match_number,
        "home_team": home,
        "away_team": away,
        "resolved": False,
        "winner": None,
    }


def _resolve_stage(
    model,
    rankings,
    stage: str,
    stage_matches: list[dict],
    match_numbers: list[int],
    slot_feeds: dict[int, tuple[str | None, str | None]],
) -> tuple[list[dict], dict[int, str], dict[int, str]]:
    """Resolves one knockout stage while preserving the official bracket slots."""
    stage_results = []
    winners: dict[int, str] = {}
    losers: dict[int, str] = {}

    for match_number, match in zip(match_numbers, stage_matches):
        home = _team_name(match["home_team"])
        away = _team_name(match["away_team"])
        home, away = _fill_missing_teams(home, away, slot_feeds.get(match_number, (None, None)))

        if home is None or away is None:
            stage_results.append(_unresolved_result(match_number, home, away))
            continue

        if match["status"] == "FINISHED":
            winner, loser = _decide_winner_loser(match, home, away)
            stage_results.append(
                {
                    "match_number": match_number,
                    "home_team": home,
                    "away_team": away,
                    "resolved": True,
                    "source": "actual_result",
                    "winner": winner,
                    "home_score": match["home_score"],
                    "away_score": match["away_score"],
                }
            )
        else:
            try:
                result = predict_match(model, rankings, home, away, stage)
            except PredictionError:
                stage_results.append(_unresolved_result(match_number, home, away))
                continue

            winner = home if result["prediction"] != "away_win" else away
            loser = away if winner == home else home
            stage_results.append(
                {
                    "match_number": match_number,
                    "home_team": home,
                    "away_team": away,
                    "resolved": True,
                    "source": "predicted",
                    "winner": winner,
                    "probabilities": result["probabilities"],
                }
            )

        winners[match_number] = winner
        losers[match_number] = loser

    return stage_results, winners, losers


def simulate_knockout_stages(model, rankings, matches: list[dict]) -> dict:
    """Simulates the knockout bracket using the official 2026 match feeds."""
    by_stage = {stage: [] for stage in KNOCKOUT_STAGES}
    for match in matches:
        if match["stage"] in by_stage:
            by_stage[match["stage"]].append(match)
    for stage_matches in by_stage.values():
        stage_matches.sort(key=lambda m: m["utc_date"])

    winners_by_match_number: dict[int, str] = {}
    losers_by_match_number: dict[int, str] = {}
    rounds = []
    champion = None

    for stage in KNOCKOUT_STAGES:
        match_numbers = _match_numbers_for_stage(stage, by_stage[stage])
        feed_map = LOSER_FEEDS if stage == "THIRD_PLACE" else WINNER_FEEDS
        source_map = losers_by_match_number if stage == "THIRD_PLACE" else winners_by_match_number
        slot_feeds = {
            match_number: (
                source_map.get(feed_map[match_number][0]),
                source_map.get(feed_map[match_number][1]),
            )
            for match_number in match_numbers
            if match_number in feed_map
        }

        stage_results, winners, losers = _resolve_stage(
            model, rankings, stage, by_stage[stage], match_numbers, slot_feeds
        )
        rounds.append({"stage": stage, "matches": stage_results})

        winners_by_match_number.update(winners)
        losers_by_match_number.update(losers)

        if stage == "FINAL" and stage_results and stage_results[-1]["resolved"]:
            champion = stage_results[-1]["winner"]

    return {"rounds": rounds, "champion": champion}
