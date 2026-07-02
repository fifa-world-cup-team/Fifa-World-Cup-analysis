"use client";

import { useState } from "react";
import { fetchPrediction, probabilityLabels, resultLabel, type Match, type Prediction } from "@/lib/api";
import { TeamBadge } from "./TeamBadge";

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function StatusBadge({ status }: { status: string }) {
  if (status === "FINISHED") {
    return (
      <span className="rounded-full bg-zinc-700/60 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-zinc-300">
        Terminé
      </span>
    );
  }
  if (status === "IN_PLAY" || status === "LIVE" || status === "PAUSED") {
    return (
      <span className="flex items-center gap-1 rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-red-300 ring-1 ring-red-500/40">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-red-400" />
        En direct
      </span>
    );
  }
  return (
    <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-300 ring-1 ring-amber-500/30">
      À venir
    </span>
  );
}

export function MatchRow({ match }: { match: Match }) {
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canPredict = Boolean(match.home_team && match.away_team) && match.status !== "FINISHED";
  const isFinished = match.status === "FINISHED";

  async function handlePredict() {
    if (!match.home_team || !match.away_team) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchPrediction(match.home_team.name, match.away_team.name, match.stage);
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-2 rounded-xl px-3 py-3 transition-colors hover:bg-emerald-900/20">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="w-2/5">
          <TeamBadge team={match.home_team} />
        </span>

        <span className="flex shrink-0 flex-col items-center gap-1">
          {isFinished ? (
            <span className="rounded-lg bg-emerald-950/80 px-3 py-1 text-base font-bold text-emerald-50 ring-1 ring-emerald-700/50">
              {match.home_score} - {match.away_score}
            </span>
          ) : (
            <span className="text-xs font-medium text-emerald-200/60">
              {formatDate(match.utc_date)}
            </span>
          )}
          <StatusBadge status={match.status} />
        </span>

        <span className="w-2/5">
          <TeamBadge team={match.away_team} align="right" />
        </span>
      </div>

      {canPredict && (
        <div className="flex flex-wrap items-center gap-2 pl-1 text-xs">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="rounded-full bg-emerald-500 px-3 py-1 font-semibold text-emerald-950 transition-colors hover:bg-emerald-400 disabled:opacity-50"
          >
            {loading ? "..." : prediction ? "Re-prédire" : "⚡ Prédire"}
          </button>

          {error && <span className="text-red-300">{error}</span>}

          {prediction && match.home_team && match.away_team && (
            <span className="flex flex-wrap items-center gap-2 rounded-lg bg-emerald-950/60 px-2.5 py-1 text-emerald-100">
              <strong className="text-emerald-300">
                {resultLabel(prediction.prediction, match.home_team.name, match.away_team.name)}
              </strong>
              {probabilityLabels(prediction.probabilities, match.home_team.name, match.away_team.name).map(
                ({ label, value }) => (
                  <span key={label} className="text-emerald-100/70">
                    {label}: {(value * 100).toFixed(0)}%
                  </span>
                ),
              )}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
