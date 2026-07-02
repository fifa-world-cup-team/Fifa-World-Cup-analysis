"use client";

import { useEffect, useState } from "react";
import { fetchMatches, fetchStandings, type GroupStanding, type Match } from "@/lib/api";
import { MatchesSection } from "@/components/MatchesSection";
import { StandingsSection } from "@/components/StandingsSection";
import { PredictorForm } from "@/components/PredictorForm";
import { TournamentSection } from "@/components/TournamentSection";

const REFRESH_INTERVAL_MS = 60_000;

export function HomeClient() {
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
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#0d3b2a,_#06120c_60%)] pb-20 font-sans">
      <header className="border-b border-emerald-900/40 bg-gradient-to-r from-emerald-950 via-emerald-900 to-emerald-950">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-8">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🏆</span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                World Cup Predictor <span className="text-emerald-400">2026</span>
              </h1>
              <p className="text-sm text-emerald-200/80">
                Matchs, classements et pronostics en direct — propulsé par notre modèle ML.
              </p>
            </div>
          </div>
          {lastUpdated && (
            <span className="flex items-center gap-2 rounded-full bg-emerald-900/60 px-3 py-1 text-xs font-medium text-emerald-200 ring-1 ring-emerald-400/30">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Mis à jour à {lastUpdated.toLocaleTimeString("fr-FR")}
            </span>
          )}
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-6 px-4 pt-8">
        {loading && (
          <p className="text-sm text-emerald-100/70">Chargement des données en direct...</p>
        )}

        {error && (
          <p className="rounded-xl bg-red-950/60 px-4 py-3 text-sm text-red-200 ring-1 ring-red-800">
            {error}
          </p>
        )}

        {!loading && !error && (
          <>
            <TournamentSection />
            <MatchesSection matches={matches} />
            <StandingsSection groups={groups} />
            <PredictorForm groups={groups} />
          </>
        )}
      </main>
    </div>
  );
}
