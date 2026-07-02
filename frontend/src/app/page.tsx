"use client";

import { useEffect, useState } from "react";
import { fetchMatches, fetchStandings, type GroupStanding, type Match } from "@/lib/api";
import { MatchesSection } from "@/components/MatchesSection";
import { StandingsSection } from "@/components/StandingsSection";
import { PredictorForm } from "@/components/PredictorForm";

const REFRESH_INTERVAL_MS = 60_000;

export default function Home() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [groups, setGroups] = useState<GroupStanding[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [matchesData, standingsData] = await Promise.all([
          fetchMatches(),
          fetchStandings(),
        ]);
        if (cancelled) return;
        setMatches(matchesData);
        setGroups(standingsData);
        setError(null);
        setLastUpdated(new Date());
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Erreur inconnue.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    const interval = setInterval(load, REFRESH_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-zinc-50 px-4 py-10 font-sans dark:bg-black">
      <main className="mx-auto flex max-w-5xl flex-col gap-6">
        <header className="flex flex-wrap items-baseline justify-between gap-2">
          <div>
            <h1 className="text-3xl font-semibold text-zinc-900 dark:text-zinc-50">
              World Cup Predictor 2026
            </h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Matchs, classements et pronostics en direct.
            </p>
          </div>
          {lastUpdated && (
            <p className="text-xs text-zinc-400">
              Mis à jour à {lastUpdated.toLocaleTimeString("fr-FR")}
            </p>
          )}
        </header>

        {loading && <p className="text-sm text-zinc-500">Chargement des données en direct...</p>}

        {error && (
          <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}

        {!loading && !error && (
          <>
            <MatchesSection matches={matches} />
            <StandingsSection groups={groups} />
            <PredictorForm groups={groups} />
          </>
        )}
      </main>
    </div>
  );
}
