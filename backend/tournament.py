from backend.model_service import PredictionError, predict_match

KNOCKOUT_STAGES = [
    "LAST_32",
    "LAST_16",
    "QUARTER_FINALS",
    "SEMI_FINALS",
    "THIRD_PLACE",
    "FINAL",
]


def _team_name(team: dict | None) -> str | None:
    return team["name"] if team else None


def _decide_winner_loser(match: dict, home: str, away: str) -> tuple[str, str]:
    if match["home_score"] is not None and match["home_score"] > match["away_score"]:
        return home, away
    if match["away_score"] is not None and match["away_score"] > match["home_score"]:
        return away, home
    return home, away


def _known_teams(stage_matches: list[dict]) -> list[str]:
    teams = []
    for match in stage_matches:
        for team in (_team_name(match["home_team"]), _team_name(match["away_team"])):
            if team:
                teams.append(team)
    return teams


def _resolve_stage(
    model,
    rankings,
    stage: str,
    stage_matches: list[dict],
    source_pool: list[str],
) -> tuple[list[dict], list[str], list[str]]:
    """Resolves one knockout stage.

    Matches with both teams already known (from the API) are left as-is.
    Matches missing a team are filled from `source_pool` (winners/losers
    carried over from the previous stage), after removing any team from the
    pool that's already accounted for by a directly-known fixture in this
    same stage — otherwise a team already assigned to a real match could be
    popped again into a different, still-unresolved slot.
    """
    available = list(source_pool)
    for team in _known_teams(stage_matches):
        if team in available:
            available.remove(team)

    stage_results = []
    winners: list[str] = []
    losers: list[str] = []

    for match in stage_matches:
        home = _team_name(match["home_team"])
        away = _team_name(match["away_team"])

        if home is None and available:
            home = available.pop(0)
        if away is None and available:
            away = available.pop(0)

        if home is None or away is None:
            stage_results.append(
                {"home_team": home, "away_team": away, "resolved": False, "winner": None}
            )
            continue

        if match["status"] == "FINISHED":
            winner, loser = _decide_winner_loser(match, home, away)
            stage_results.append(
                {
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
                stage_results.append(
                    {"home_team": home, "away_team": away, "resolved": False, "winner": None}
                )
                continue

            winner = home if result["prediction"] != "away_win" else away
            loser = away if winner == home else home
            stage_results.append(
                {
                    "home_team": home,
                    "away_team": away,
                    "resolved": True,
                    "source": "predicted",
                    "winner": winner,
                    "probabilities": result["probabilities"],
                }
            )

        winners.append(winner)
        losers.append(loser)

    return stage_results, winners, losers


def simulate_knockout_stages(model, rankings, matches: list[dict]) -> dict:
    """Simulates the knockout bracket forward using the trained model for any
    match whose two teams are already known but not yet finished. This is an
    approximation, not an official bracket: unresolved slots are filled by
    chaining winners/losers from earlier rounds in date order, since the API
    does not expose which specific earlier match feeds which later slot.
    """
    by_stage = {stage: [] for stage in KNOCKOUT_STAGES}
    for match in matches:
        if match["stage"] in by_stage:
            by_stage[match["stage"]].append(match)
    for stage_matches in by_stage.values():
        stage_matches.sort(key=lambda m: m["utc_date"])

    winners_pool: list[str] = []
    losers_pool: list[str] = []
    semi_final_winners: list[str] = []
    rounds = []
    champion = None

    for stage in KNOCKOUT_STAGES:
        if stage == "THIRD_PLACE":
            source_pool = losers_pool
        elif stage == "FINAL":
            source_pool = semi_final_winners
        else:
            source_pool = winners_pool

        stage_results, winners, losers = _resolve_stage(
            model, rankings, stage, by_stage[stage], source_pool
        )
        rounds.append({"stage": stage, "matches": stage_results})

        if stage == "SEMI_FINALS":
            semi_final_winners = winners
            losers_pool = losers
        winners_pool = winners

        if stage == "FINAL" and stage_results and stage_results[-1]["resolved"]:
            champion = stage_results[-1]["winner"]

    return {"rounds": rounds, "champion": champion}
