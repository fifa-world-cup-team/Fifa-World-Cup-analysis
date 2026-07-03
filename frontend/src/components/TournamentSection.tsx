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
  const matches = matchNumbers
    .map((matchNumber) => round.matches.find((match) => match.match_number === matchNumber))
    .filter((match): match is TournamentMatch => Boolean(match));

  if (matches.length === 0) return null;
  return { stage, matches };
}

function toMatchPairs(matches: TournamentMatch[]) {
  const pairs: TournamentMatch[][] = [];
  for (let index = 0; index < matches.length; index += 2) {
    pairs.push(matches.slice(index, index + 2));
  }
  return pairs;
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
        "flex min-h-5 items-center justify-between gap-1 rounded-md px-1.5 py-0.5 text-[10px]",
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
  connectLeft = false,
  connectRight = false,
}: {
  match: TournamentMatch;
  connectLeft?: boolean;
  connectRight?: boolean;
}) {
  const status =
    match.source === "actual_result" ? "reel" : match.source === "predicted" ? "predit" : "a venir";
  const score = scoreLabel(match);

  return (
    <article className="relative h-[90px] w-[120px] overflow-hidden rounded-lg border border-emerald-700/35 bg-emerald-950/80 p-1.5 shadow-md shadow-black/20">
      {connectRight && (
        <span className="pointer-events-none absolute left-full top-1/2 hidden h-px w-2 bg-emerald-400/45 lg:block" />
      )}
      {connectLeft && (
        <span className="pointer-events-none absolute right-full top-1/2 hidden h-px w-2 bg-emerald-400/45 lg:block" />
      )}
      <div className="mb-1 flex items-center justify-between gap-1 text-[8px] uppercase tracking-wide">
        <span className="rounded-full bg-emerald-900/80 px-1.5 py-0.5 text-emerald-200/70">
          {match.match_number ? `M${match.match_number}` : status}
        </span>
        <span className="text-emerald-300/60">{status}</span>
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
      {match.winner && (
        <p className="mt-1 truncate text-[9px] font-semibold text-amber-100">
          Vainqueur: {match.winner}
        </p>
      )}
    </article>
  );
}

function BracketColumn({
  round,
  index,
  side,
  columnIndex,
  columnCount,
}: {
  round: TournamentRound;
  index: number;
  side: "left" | "right";
  columnIndex: number;
  columnCount: number;
}) {
  const pairGap = Math.min(14 * 2 ** index, 108);
  const innerGap = 14;
  const connectLeft = side === "left" ? columnIndex > 0 : true;
  const connectRight = side === "left" ? true : columnIndex < columnCount - 1;
  const mergeSide = side === "left" ? "right" : "left";
  const pairs = toMatchPairs(round.matches);

  return (
    <div className="flex w-[120px] flex-col">
      <h3 className="mb-2 text-center text-[10px] font-bold uppercase tracking-widest text-emerald-300/70">
        {SHORT_STAGE_LABELS[round.stage] ?? STAGE_LABELS[round.stage] ?? round.stage}
      </h3>
      <div className="flex flex-1 flex-col justify-center" style={{ gap: pairGap }}>
        {pairs.map((pair, pairIndex) => {
          const hasPairConnector = pair.length === 2 && (connectLeft || connectRight);
          return (
            <div
              key={`${round.stage}-pair-${pairIndex}`}
              className="relative flex flex-col"
              style={{ gap: innerGap }}
            >
              {hasPairConnector && (
                <span
                  className={[
                    "pointer-events-none absolute bottom-[45px] top-[45px] hidden w-px bg-emerald-400/45 lg:block",
                    mergeSide === "right"
                      ? "left-[calc(100%+0.5rem)]"
                      : "right-[calc(100%+0.5rem)]",
                  ].join(" ")}
                />
              )}
              {pair.map((match, matchIndex) => (
                <MatchCard
                  key={`${round.stage}-${match.match_number ?? `${pairIndex}-${matchIndex}`}`}
                  match={match}
                  connectLeft={connectLeft}
                  connectRight={connectRight}
                />
              ))}
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
    <div className="flex items-stretch gap-4">
      {sideRounds.map((round, index) => {
        const spacingIndex = side === "left" ? index : sideRounds.length - index - 1;
        return (
          <BracketColumn
            key={`${side}-${round.stage}`}
            round={round}
            index={spacingIndex}
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
    <div className="flex w-[132px] flex-col items-center justify-center">
      <h3 className="mb-2 text-center text-[10px] font-bold uppercase tracking-widest text-amber-300/80">
        Finale
      </h3>
      <div className="rounded-xl border border-amber-400/40 bg-amber-500/10 p-1.5 shadow-lg shadow-amber-950/30">
        {finalMatch ? (
          <MatchCard match={finalMatch} connectLeft connectRight />
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
        Le bracket n'est pas encore disponible.
      </p>
    );
  }

  return (
    <div className="mt-5">
      <div className="overflow-x-hidden rounded-2xl border border-emerald-800/40 bg-black/15 p-3">
        <div className="flex w-full min-w-[1180px] items-stretch justify-center gap-4">
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
          <MatchCard match={thirdPlace.matches[0]} />
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
        resultat, les tours a venir sont predits. Le tableau respecte les parties officielles du
        bracket 2026 pour eviter les matchs impossibles.
      </p>

      {!data ? (
        <p className="mt-4 text-sm text-emerald-200/60">Simulation en cours...</p>
      ) : (
        <>
          <div className="mt-4 flex items-center gap-4 rounded-xl bg-gradient-to-r from-amber-500/20 to-yellow-400/10 px-5 py-4 ring-1 ring-amber-400/30">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-300/20 text-xs font-black uppercase tracking-wide text-amber-100 ring-1 ring-amber-200/40">
              FIFA
            </span>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-300">
                Champion predit
              </p>
              <p className="text-3xl font-extrabold text-amber-100">
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
