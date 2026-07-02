"use client";

import { useEffect, useState } from "react";
import { fetchTournament, STAGE_LABELS, type TournamentResult } from "@/lib/api";

export function TournamentSection() {
  const [data, setData] = useState<TournamentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchTournament()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Erreur inconnue.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Simulation : qui va gagner la Coupe du Monde ?
      </h2>
      <p className="mt-1 text-xs text-zinc-500">
        Simulation approximative basée sur notre modèle : les tours déjà joués utilisent le
        vrai résultat, les tours à venir sont prédits. Certains tours ne sont pas encore
        officiellement tirés au sort par la FIFA — dans ce cas on enchaîne les vainqueurs dans
        l&apos;ordre chronologique, ce n&apos;est pas forcément le vrai bracket.
      </p>

      {!data ? (
        <p className="mt-4 text-sm text-zinc-500">Simulation en cours...</p>
      ) : (
        <>
          <div className="mt-4 rounded-xl bg-gradient-to-r from-amber-50 to-amber-100 px-5 py-4 dark:from-amber-950 dark:to-amber-900">
            <p className="text-xs uppercase tracking-wide text-amber-700 dark:text-amber-400">
              Champion prédit
            </p>
            <p className="text-2xl font-bold text-amber-900 dark:text-amber-200">
              {data.champion ?? "Pas encore déterminable"}
            </p>
          </div>

          <button
            onClick={() => setExpanded((v) => !v)}
            className="mt-3 text-sm font-medium text-zinc-600 underline dark:text-zinc-400"
          >
            {expanded ? "Masquer le détail des tours" : "Voir le détail des tours"}
          </button>

          {expanded && (
            <div className="mt-4 flex flex-col gap-4">
              {data.rounds.map((round) => (
                <div key={round.stage}>
                  <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-400">
                    {STAGE_LABELS[round.stage] ?? round.stage}
                  </h3>
                  {round.matches.map((match, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between border-b border-zinc-100 py-1.5 text-sm dark:border-zinc-800"
                    >
                      <span>
                        {match.home_team ?? "?"} vs {match.away_team ?? "?"}
                      </span>
                      <span className="font-medium text-zinc-700 dark:text-zinc-300">
                        {match.winner ?? "À déterminer"}
                        {match.source === "predicted" && (
                          <span className="ml-1 text-xs text-zinc-400">(prédit)</span>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
