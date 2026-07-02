"use client";

import { useMemo, useState } from "react";
import { fetchPrediction, RESULT_LABELS, type GroupStanding, type Prediction } from "@/lib/api";

const STAGES = [
  "GROUP_STAGE",
  "LAST_32",
  "LAST_16",
  "QUARTER_FINALS",
  "SEMI_FINALS",
  "FINAL",
];

export function PredictorForm({ groups }: { groups: GroupStanding[] }) {
  const teams = useMemo(() => {
    const names = groups.flatMap((group) => group.table.map((row) => row.team));
    return Array.from(new Set(names)).sort((a, b) => a.localeCompare(b));
  }, [groups]);

  const [homeTeam, setHomeTeam] = useState(teams[0] ?? "");
  const [awayTeam, setAwayTeam] = useState(teams[1] ?? "");
  const [stage, setStage] = useState(STAGES[0]);
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await fetchPrediction(homeTeam, awayTeam, stage));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    } finally {
      setLoading(false);
    }
  }

  if (teams.length === 0) {
    return null;
  }

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-1 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Simuler un match
      </h2>
      <p className="mb-4 text-sm text-zinc-500">
        Choisis deux équipes qualifiées pour voir ce que prédit le modèle.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 text-sm text-zinc-700 dark:text-zinc-300">
          Domicile
          <select
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
            className="rounded-lg border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-800"
          >
            {teams.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm text-zinc-700 dark:text-zinc-300">
          Extérieur
          <select
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
            className="rounded-lg border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-800"
          >
            {teams.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm text-zinc-700 dark:text-zinc-300">
          Stade
          <select
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            className="rounded-lg border border-zinc-300 bg-white px-3 py-2 dark:border-zinc-700 dark:bg-zinc-800"
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
          className="rounded-full bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {loading ? "..." : "Prédire"}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}

      {result && (
        <div className="mt-4 rounded-lg bg-zinc-100 px-4 py-3 text-sm dark:bg-zinc-800">
          <strong>{RESULT_LABELS[result.prediction] ?? result.prediction}</strong>
          <ul className="mt-1 flex gap-4 text-zinc-600 dark:text-zinc-400">
            {Object.entries(result.probabilities).map(([label, value]) => (
              <li key={label}>
                {RESULT_LABELS[label] ?? label}: {(value * 100).toFixed(1)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
