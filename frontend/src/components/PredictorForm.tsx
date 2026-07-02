"use client";

import { useMemo, useState } from "react";
import { fetchPrediction, probabilityLabels, resultLabel, type GroupStanding, type Prediction } from "@/lib/api";

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

  const crests = useMemo(() => {
    const map = new Map<string, string | null>();
    for (const group of groups) {
      for (const row of group.table) {
        map.set(row.team, row.crest);
      }
    }
    return map;
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

  const selectClass =
    "w-full appearance-none rounded-xl border border-emerald-800/50 bg-emerald-950/70 px-3 py-2.5 font-medium text-emerald-50 outline-none ring-emerald-500/40 focus:ring-2";

  return (
    <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6 shadow-lg shadow-black/20 backdrop-blur-sm">
      <h2 className="mb-1 flex items-center gap-2 text-lg font-semibold text-emerald-50">
        🎮 Simuler un match
      </h2>
      <p className="mb-4 text-sm text-emerald-200/50">
        Choisis deux équipes qualifiées pour voir ce que prédit le modèle.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col items-center gap-3 sm:flex-row">
          <div className="flex w-full items-center gap-2 sm:w-2/5">
            {crests.get(homeTeam) && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={crests.get(homeTeam)!} alt="" className="h-8 w-8 shrink-0 object-contain" />
            )}
            <select value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)} className={selectClass}>
              {teams.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>

          <span className="shrink-0 text-sm font-bold text-amber-400">VS</span>

          <div className="flex w-full items-center gap-2 sm:w-2/5">
            {crests.get(awayTeam) && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={crests.get(awayTeam)!} alt="" className="h-8 w-8 shrink-0 object-contain" />
            )}
            <select value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)} className={selectClass}>
              {teams.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            className="rounded-xl border border-emerald-800/50 bg-emerald-950/70 px-3 py-2 text-sm text-emerald-50 outline-none ring-emerald-500/40 focus:ring-2"
          >
            {STAGES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <button
            type="submit"
            disabled={loading || homeTeam === awayTeam}
            className="rounded-full bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-emerald-950 transition-colors hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "..." : "⚡ Prédire"}
          </button>
        </div>
      </form>

      {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

      {result && (
        <div className="mt-4 rounded-xl bg-emerald-900/40 px-4 py-3 text-sm ring-1 ring-emerald-700/40">
          <strong className="text-emerald-200">
            {resultLabel(result.prediction, homeTeam, awayTeam)}
          </strong>
          <ul className="mt-1 flex flex-wrap gap-4 text-emerald-100/70">
            {probabilityLabels(result.probabilities, homeTeam, awayTeam).map(({ label, value }) => (
              <li key={label}>
                {label}: {(value * 100).toFixed(1)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
