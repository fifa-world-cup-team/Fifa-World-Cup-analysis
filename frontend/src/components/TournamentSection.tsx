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

function getBracketRounds(rounds: TournamentRound[]) {
  const byStage = new Map(rounds.map((round) => [round.stage, round]));

  return BRACKET_STAGES.map((stage) => byStage.get(stage))
    .filter((round): round is TournamentRound => Boolean(round))
    .filter((round) => round.matches.length > 0);
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
        "flex min-h-8 items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-xs",
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

function MatchCard({ match, isFinal }: { match: TournamentMatch; isFinal: boolean }) {
  const status =
    match.source === "actual_result" ? "reel" : match.source === "predicted" ? "predit" : "a venir";
  const score = scoreLabel(match);

  return (
    <article className="relative min-w-[170px] rounded-xl border border-emerald-700/35 bg-emerald-950/80 p-2 shadow-md shadow-black/20">
      {!isFinal && (
        <span className="pointer-events-none absolute left-full top-1/2 hidden h-px w-6 bg-emerald-400/35 lg:block" />
      )}
      <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-wide">
        <span className="rounded-full bg-emerald-900/80 px-2 py-0.5 text-emerald-200/70">
          {status}
        </span>
        {score && <span className="font-semibold text-amber-200">{score}</span>}
      </div>
      <div className="flex flex-col gap-1.5">
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
        <p className="mt-2 truncate text-[11px] font-semibold text-amber-100">
          Vainqueur: {match.winner}
        </p>
      )}
    </article>
  );
}

function BracketColumn({
  round,
  index,
  isFinal,
}: {
  round: TournamentRound;
  index: number;
  isFinal: boolean;
}) {
  const gap = Math.min(12 * 2 ** index, 96);

  return (
    <div className="flex min-w-[190px] flex-col">
      <h3 className="mb-3 text-center text-xs font-bold uppercase tracking-widest text-emerald-300/70">
        {SHORT_STAGE_LABELS[round.stage] ?? STAGE_LABELS[round.stage] ?? round.stage}
      </h3>
      <div className="flex flex-1 flex-col justify-center" style={{ gap }}>
        {round.matches.map((match, matchIndex) => (
          <MatchCard
            key={`${round.stage}-${matchIndex}`}
            match={match}
            isFinal={isFinal}
          />
        ))}
      </div>
    </div>
  );
}

function TournamentBracket({ data }: { data: TournamentResult }) {
  const rounds = getBracketRounds(data.rounds);
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
      <div className="overflow-x-auto rounded-2xl border border-emerald-800/40 bg-black/15 p-4">
        <div className="flex min-w-max items-stretch gap-6">
          {rounds.map((round, index) => (
            <BracketColumn
              key={round.stage}
              round={round}
              index={index}
              isFinal={index === rounds.length - 1}
            />
          ))}
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
    <section className="rounded-2xl border border-amber-700/30 bg-gradient-to-br from-emerald-950/60 to-amber-950/20 p-6 shadow-lg shadow-black/20 backdrop-blur-sm">
      <h2 className="flex items-center gap-2 text-lg font-semibold text-emerald-50">
        Qui va gagner la Coupe du Monde ?
      </h2>
      <p className="mt-1 text-xs text-emerald-200/50">
        Simulation approximative basee sur notre modele : les tours deja joues utilisent le vrai
        resultat, les tours a venir sont predits. Certains tours ne sont pas encore officiellement
        tires au sort par la FIFA, donc le bracket reste indicatif.
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
