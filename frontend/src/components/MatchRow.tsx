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
    <div className="flex flex-col gap-2 border-b border-zinc-100 py-3 last:border-none dark:border-zinc-800">
      <div className="flex items-center justify-between gap-4 text-sm">
        <span className="w-1/3">
          <TeamBadge team={match.home_team} />
        </span>

        <span className="shrink-0 text-center font-semibold text-zinc-700 dark:text-zinc-300">
          {isFinished ? (
            `${match.home_score} - ${match.away_score}`
          ) : (
            <span className="text-xs text-zinc-400">{formatDate(match.utc_date)}</span>
          )}
        </span>

        <span className="w-1/3">
          <TeamBadge team={match.away_team} align="right" />
        </span>
      </div>

      {canPredict && (
        <div className="flex items-center gap-3 pl-1 text-xs">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="rounded-full bg-zinc-900 px-3 py-1 font-medium text-white transition-colors hover:bg-zinc-700 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
          >
            {loading ? "..." : prediction ? "Re-prédire" : "Prédire"}
          </button>

          {error && <span className="text-red-600 dark:text-red-400">{error}</span>}

          {prediction && match.home_team && match.away_team && (
            <span className="flex gap-2 text-zinc-600 dark:text-zinc-400">
              <strong>
                {resultLabel(prediction.prediction, match.home_team.name, match.away_team.name)}
              </strong>
              {probabilityLabels(prediction.probabilities, match.home_team.name, match.away_team.name).map(
                ({ label, value }) => (
                  <span key={label}>
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
