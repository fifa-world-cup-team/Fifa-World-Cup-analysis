"use client";

import { useEffect, useState } from "react";
import {
  fetchTournament,
  STAGE_LABELS,
  type TournamentMatch,
  type TournamentResult,
  type TournamentRound,
} from "@/lib/api";

const REFRESH_INTERVAL_MS = 60_000;
const BRACKET_STAGES = ["LAST_32", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"];
const SHORT_STAGE_LABELS: Record<string, string> = {
  LAST_32: "R32",
  LAST_16: "R16",
  ROUND_OF_16: "R16",
  QUARTER_FINALS: "QF",
  SEMI_FINALS: "SF",
  FINAL: "Finale",
};
const STAGE_MATCH_NUMBERS_BY_DATE: Record<string, number[]> = {
  LAST_32: [73, 78, 74, 75, 76, 77, 79, 80, 82, 81, 84, 83, 85, 88, 86, 87],
  LAST_16: [90, 89, 91, 92, 93, 94, 95, 96],
  QUARTER_FINALS: [97, 99, 98, 100],
  SEMI_FINALS: [101, 102],
  FINAL: [104],
};
const LEFT_BRACKET_MATCHES: Record<string, number[]> = {
  LAST_32: [74, 77, 73, 75, 83, 84, 81, 82],
  LAST_16: [89, 90, 93, 94],
  QUARTER_FINALS: [97, 98],
  SEMI_FINALS: [101],
};
const RIGHT_BRACKET_MATCHES: Record<string, number[]> = {
  LAST_32: [76, 78, 79, 80, 86, 88, 85, 87],
  LAST_16: [91, 92, 95, 96],
  QUARTER_FINALS: [99, 100],
  SEMI_FINALS: [102],
};
const SIDE_STAGES = ["LAST_32", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS"];

function getBracketRounds(rounds: TournamentRound[]) {
  const byStage = new Map(rounds.map((round) => [round.stage, round]));

  return BRACKET_STAGES.map((stage) => byStage.get(stage))
    .filter((round): round is TournamentRound => Boolean(round))
    .filter((round) => round.matches.length > 0);
}

function getRoundByStage(rounds: TournamentRound[], stage: string) {
  return rounds.find((round) => round.stage === stage);
}

function getSideRound(
  rounds: TournamentRound[],
  stage: string,
  sideMatches: Record<string, number[]>,
): TournamentRound | null {
  const round = getRoundByStage(rounds, stage);
  if (!round) return null;

  const matchNumbers = sideMatches[stage] ?? [];
  const fallbackOrder = STAGE_MATCH_NUMBERS_BY_DATE[stage] ?? [];
  const matches = matchNumbers
    .map((matchNumber) => {
      const directMatch = round.matches.find((match) => match.match_number === matchNumber);
      if (directMatch) return directMatch;

      const fallbackIndex = fallbackOrder.indexOf(matchNumber);
      const fallbackMatch = fallbackIndex >= 0 ? round.matches[fallbackIndex] : undefined;
      return fallbackMatch ? { ...fallbackMatch, match_number: matchNumber } : undefined;
    })
    .filter((match): match is TournamentMatch => Boolean(match));

  if (matches.length === 0) return null;
  return { stage, matches };
}

function scoreLabel(match: TournamentMatch) {
  if (match.home_score === undefined || match.away_score === undefined) return null;
  return `${match.home_score}-${match.away_score}`;
}

function TeamRow({
  name,
  score,
  isWinner,
}: {
  name: string | null;
  score?: number;
  isWinner: boolean;
}) {
  return (
    <div
      className={[
        "flex min-h-6 items-center justify-between gap-1.5 rounded-md px-2 py-0.5 text-[11px]",
        isWinner
          ? "bg-amber-400/20 font-bold text-amber-50 ring-1 ring-amber-300/40"
          : "bg-emerald-950/70 text-emerald-100/75 ring-1 ring-emerald-800/40",
      ].join(" ")}
    >
      <span className="truncate">{name ?? "A determiner"}</span>
      {score !== undefined && <span className="shrink-0 text-emerald-50/80">{score}</span>}
    </div>
  );
}

function MatchCard({
  match,
  isFinal = false,
  connectLeft = false,
  connectRight = false,
}: {
  match: TournamentMatch;
  isFinal?: boolean;
  connectLeft?: boolean;
  connectRight?: boolean;
}) {
  const status =
    match.source === "actual_result" ? "reel" : match.source === "predicted" ? "predit" : "a venir";
  const score = scoreLabel(match);

  return (
    <article
      className={[
        "relative h-[90px] w-full min-w-0 overflow-hidden rounded-lg border p-2 shadow-md shadow-black/20",
        isFinal
          ? "border-amber-400/45 bg-amber-500/10"
          : "border-emerald-700/35 bg-emerald-950/80",
      ].join(" ")}
    >
      {connectLeft && (
        <span className="pointer-events-none absolute right-full top-1/2 hidden h-px w-3 bg-emerald-400/45 lg:block" />
      )}
      {connectRight && (
        <span className="pointer-events-none absolute left-full top-1/2 hidden h-px w-3 bg-emerald-400/45 lg:block" />
      )}
      <div className="mb-1.5 flex items-center justify-between text-[9px] uppercase tracking-wide">
        <span className="rounded-full bg-emerald-900/80 px-1.5 py-0.5 text-emerald-200/70">
          {match.match_number ? `M${match.match_number}` : status}
        </span>
        {score && <span className="font-semibold text-amber-200">{score}</span>}
      </div>
      <div className="flex flex-col gap-1">
        <TeamRow
          name={match.home_team}
          score={match.home_score}
          isWinner={Boolean(match.home_team && match.winner === match.home_team)}
        />
        <TeamRow
          name={match.away_team}
          score={match.away_score}
          isWinner={Boolean(match.away_team && match.winner === match.away_team)}
        />
      </div>
    </article>
  );
}

function ForkConnector({ side }: { side: "left" | "right" }) {
  const sideClass = side === "left" ? "left-[-0.75rem]" : "right-[-0.75rem]";
  const centerArmClass =
    side === "left" ? "left-[-0.75rem]" : "right-[-0.75rem]";

  return (
    <>
      <span
        className={[
          "pointer-events-none absolute top-[24%] bottom-[24%] hidden w-px bg-emerald-400/50 lg:block",
          sideClass,
        ].join(" ")}
      />
      <span
        className={[
          "pointer-events-none absolute top-1/2 hidden h-px w-3 bg-emerald-400/50 lg:block",
          centerArmClass,
        ].join(" ")}
      />
    </>
  );
}

function BracketColumn({
  round,
  side,
  columnIndex,
  columnCount,
}: {
  round: TournamentRound;
  side: "left" | "right";
  columnIndex: number;
  columnCount: number;
}) {
  const stageProgress = SIDE_STAGES.indexOf(round.stage);
  const groupSpan = stageProgress >= 0 ? 2 ** stageProgress : 1;
  const connectLeft = side === "left" ? columnIndex > 0 : true;
  const connectRight = side === "left" ? true : columnIndex < columnCount - 1;
  const incomingSide = side === "left" ? "left" : "right";
  const showIncomingFork = groupSpan > 1;

  return (
    <div className="flex min-w-0 flex-col">
      <h3 className="mb-2 text-center text-[10px] font-bold uppercase tracking-widest text-emerald-300/70">
        {SHORT_STAGE_LABELS[round.stage] ?? STAGE_LABELS[round.stage] ?? round.stage}
      </h3>
      <div className="grid flex-1 grid-rows-8 gap-2">
        {round.matches.map((match, matchIndex) => {
          const rowStart = matchIndex * groupSpan + 1;
          return (
            <div
              key={`${round.stage}-${match.match_number ?? matchIndex}`}
              className="relative flex min-h-0 items-center"
              style={{ gridRow: `${rowStart} / span ${groupSpan}` }}
            >
              {showIncomingFork && <ForkConnector side={incomingSide} />}
              <MatchCard
                match={match}
                connectLeft={connectLeft}
                connectRight={connectRight}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}

function BracketSide({
  rounds,
  side,
}: {
  rounds: TournamentRound[];
  side: "left" | "right";
}) {
  const matchGroups = side === "left" ? LEFT_BRACKET_MATCHES : RIGHT_BRACKET_MATCHES;
  const stages = side === "left" ? SIDE_STAGES : [...SIDE_STAGES].reverse();
  const sideRounds = stages
    .map((stage) => getSideRound(rounds, stage, matchGroups))
    .filter((round): round is TournamentRound => Boolean(round));

  return (
    <div className="grid min-w-0 flex-1 grid-cols-4 gap-3">
      {sideRounds.map((round, index) => {
        return (
          <BracketColumn
            key={`${side}-${round.stage}`}
            round={round}
            side={side}
            columnIndex={index}
            columnCount={sideRounds.length}
          />
        );
      })}
    </div>
  );
}

function FinalColumn({ finalRound }: { finalRound: TournamentRound | null }) {
  const finalMatch = finalRound?.matches[0];

  return (
    <div className="flex min-w-0 flex-[0.7] flex-col items-center justify-center">
      <h3 className="mb-2 text-center text-[10px] font-bold uppercase tracking-widest text-amber-300/80">
        Finale
      </h3>
      <div className="w-full rounded-xl border border-amber-400/40 bg-amber-500/10 p-1.5 shadow-lg shadow-amber-950/30">
        {finalMatch ? (
          <MatchCard match={finalMatch} isFinal connectLeft connectRight />
        ) : (
          <p className="rounded-xl border border-amber-400/20 bg-amber-950/30 p-3 text-center text-xs text-amber-100/70">
            Finale a determiner
          </p>
        )}
      </div>
    </div>
  );
}

function TournamentBracket({ data }: { data: TournamentResult }) {
  const rounds = getBracketRounds(data.rounds);
  const finalRound = getRoundByStage(data.rounds, "FINAL") ?? null;
  const thirdPlace = data.rounds.find((round) => round.stage === "THIRD_PLACE");

  if (rounds.length === 0) {
    return (
      <p className="mt-4 rounded-xl border border-emerald-800/40 bg-emerald-950/50 p-4 text-sm text-emerald-200/60">
        Le bracket n&apos;est pas encore disponible.
      </p>
    );
  }

  return (
    <div className="mt-5">
      <div className="overflow-hidden rounded-2xl border border-emerald-800/40 bg-black/15 p-3">
        <div className="grid min-h-[760px] grid-cols-[minmax(0,1fr)_minmax(110px,0.18fr)_minmax(0,1fr)] items-stretch gap-4">
          <BracketSide rounds={data.rounds} side="left" />
          <FinalColumn finalRound={finalRound} />
          <BracketSide rounds={data.rounds} side="right" />
        </div>
      </div>

      {thirdPlace && thirdPlace.matches.length > 0 && (
        <div className="mt-4 max-w-sm rounded-xl border border-orange-400/25 bg-orange-950/20 p-3">
          <h3 className="mb-2 text-xs font-bold uppercase tracking-widest text-orange-200/80">
            Petite finale
          </h3>
          <MatchCard match={thirdPlace.matches[0]} isFinal />
        </div>
      )}
    </div>
  );
}

export function TournamentSection() {
  const [data, setData] = useState<TournamentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    function load() {
      fetchTournament()
        .then((result) => {
          if (!cancelled) {
            setData(result);
            setError(null);
          }
        })
        .catch((err) => {
          if (!cancelled) setError(err instanceof Error ? err.message : "Erreur inconnue.");
        });
    }

    load();
    const interval = setInterval(load, REFRESH_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  if (error) {
    return (
      <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6">
        <p className="text-sm text-red-300">{error}</p>
      </section>
    );
  }

  return (
    <section className="relative left-1/2 w-[calc(100vw-2rem)] -translate-x-1/2 rounded-2xl border border-amber-700/30 bg-gradient-to-br from-emerald-950/60 to-amber-950/20 p-6 shadow-lg shadow-black/20 backdrop-blur-sm">
      <h2 className="flex items-center gap-2 text-lg font-semibold text-emerald-50">
        Qui va gagner la Coupe du Monde ?
      </h2>
      <p className="mt-1 text-xs text-emerald-200/50">
        Simulation approximative basee sur notre modele : les tours deja joues utilisent le vrai
        resultat, les tours a venir sont predits. Le tableau respecte les deux parties du bracket
        2026 pour eviter les matchs impossibles.
      </p>

      {!data ? (
        <p className="mt-4 text-sm text-emerald-200/60">Simulation en cours...</p>
      ) : (
        <>
          <div className="mt-3 flex items-center gap-3 rounded-xl bg-gradient-to-r from-amber-500/20 to-yellow-400/10 px-4 py-3 ring-1 ring-amber-400/30">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-300/20 text-[10px] font-black uppercase tracking-wide text-amber-100 ring-1 ring-amber-200/40">
              FIFA
            </span>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-300">
                Champion predit
              </p>
              <p className="text-2xl font-extrabold text-amber-100">
                {data.champion ?? "Pas encore determinable"}
              </p>
            </div>
          </div>

          <TournamentBracket data={data} />
        </>
      )}
    </section>
  );
}
