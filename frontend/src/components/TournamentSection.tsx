"use client";

import { useEffect, useState } from "react";
import { fetchTournament, STAGE_LABELS, type TournamentResult } from "@/lib/api";

const REFRESH_INTERVAL_MS = 60_000;

export function TournamentSection() {
  const [data, setData] = useState<TournamentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

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
        🔮 Qui va gagner la Coupe du Monde ?
      </h2>
      <p className="mt-1 text-xs text-emerald-200/50">
        Simulation approximative basée sur notre modèle : les tours déjà joués utilisent le
        vrai résultat, les tours à venir sont prédits. Certains tours ne sont pas encore
        officiellement tirés au sort par la FIFA — dans ce cas on enchaîne les vainqueurs dans
        l&apos;ordre chronologique, ce n&apos;est pas forcément le vrai bracket.
      </p>

      {!data ? (
        <p className="mt-4 text-sm text-emerald-200/60">Simulation en cours...</p>
      ) : (
        <>
          <div className="mt-4 flex items-center gap-4 rounded-xl bg-gradient-to-r from-amber-500/20 to-yellow-400/10 px-5 py-4 ring-1 ring-amber-400/30">
            <span className="text-4xl">🏆</span>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-300">
                Champion prédit
              </p>
              <p className="text-3xl font-extrabold text-amber-100">
                {data.champion ?? "Pas encore déterminable"}
              </p>
            </div>
          </div>

          <button
            onClick={() => setExpanded((v) => !v)}
            className="mt-3 text-sm font-medium text-emerald-300 underline decoration-emerald-600 underline-offset-2 hover:text-emerald-200"
          >
            {expanded ? "Masquer le détail des tours" : "Voir le détail des tours"}
          </button>

          {expanded && (
            <div className="mt-4 flex flex-col gap-4">
              {data.rounds.map((round) => (
                <div key={round.stage}>
                  <h3 className="mb-1 text-xs font-bold uppercase tracking-widest text-emerald-400/70">
                    {STAGE_LABELS[round.stage] ?? round.stage}
                  </h3>
                  <div className="divide-y divide-emerald-900/40">
                    {round.matches.map((match, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between py-1.5 text-sm text-emerald-100/80"
                      >
                        <span>
                          {match.home_team ?? "?"} vs {match.away_team ?? "?"}
                        </span>
                        <span className="font-semibold text-emerald-50">
                          {match.winner ?? "À déterminer"}
                          {match.source === "predicted" && (
                            <span className="ml-1 text-xs font-normal text-emerald-400/60">
                              (prédit)
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}
