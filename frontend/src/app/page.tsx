"use client";

import { useState } from "react";

const TEAMS = [
  "Argentina",
  "Brazil",
  "France",
  "Germany",
  "Spain",
  "England",
  "Portugal",
  "Netherlands",
  "Italy",
  "Belgium",
  "Croatia",
  "Uruguay",
  "Colombia",
  "USA",
  "Mexico",
  "Japan",
  "Korea Republic",
  "Morocco",
  "Senegal",
  "Côte d'Ivoire",
];

const STAGES = [
  "GROUP_STAGE",
  "ROUND_OF_16",
  "QUARTER_FINALS",
  "SEMI_FINALS",
  "FINAL",
];

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "https://fifa-backend-production.onrender.com";

type PredictionResult = {
  prediction: string;
  probabilities: Record<string, number>;
};

const RESULT_LABELS: Record<string, string> = {
  home_win: "Victoire domicile",
  draw: "Match nul",
  away_win: "Victoire extérieur",
};

export default function Home() {
  const [homeTeam, setHomeTeam] = useState(TEAMS[0]);
  const [awayTeam, setAwayTeam] = useState(TEAMS[1]);
  const [stage, setStage] = useState(STAGES[0]);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          home_team: homeTeam,
          away_team: awayTeam,
          stage,
        }),
      });

      const body = await response.json();

      if (!response.ok) {
        throw new Error(body.detail ?? "La prédiction a échoué.");
      }

      setResult(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 px-4 py-16 font-sans dark:bg-black">
      <main className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <h1 className="mb-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          World Cup Predictor 2026
        </h1>
        <p className="mb-6 text-sm text-zinc-500 dark:text-zinc-400">
          Choisis deux équipes, on te donne un pronostic.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1 text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Équipe à domicile
            <select
              value={homeTeam}
              onChange={(event) => setHomeTeam(event.target.value)}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
            >
              {TEAMS.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-1 text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Équipe à l&apos;extérieur
            <select
              value={awayTeam}
              onChange={(event) => setAwayTeam(event.target.value)}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
            >
              {TEAMS.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-1 text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Stade de la compétition
            <select
              value={stage}
              onChange={(event) => setStage(event.target.value)}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
            >
              {STAGES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>

          <button
            type="submit"
            disabled={loading || homeTeam === awayTeam}
            className="mt-2 rounded-full bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-300"
          >
            {loading ? "Prédiction en cours..." : "Prédire le match"}
          </button>

          {homeTeam === awayTeam && (
            <p className="text-sm text-amber-600 dark:text-amber-400">
              Choisis deux équipes différentes.
            </p>
          )}
        </form>

        {error && (
          <p className="mt-6 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}

        {result && (
          <div className="mt-6 rounded-lg bg-zinc-100 px-4 py-4 dark:bg-zinc-800">
            <p className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
              {RESULT_LABELS[result.prediction] ?? result.prediction}
            </p>
            <ul className="mt-3 flex flex-col gap-1 text-sm text-zinc-600 dark:text-zinc-400">
              {Object.entries(result.probabilities).map(([label, value]) => (
                <li key={label} className="flex justify-between">
                  <span>{RESULT_LABELS[label] ?? label}</span>
                  <span>{(value * 100).toFixed(1)}%</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>
    </div>
  );
}
