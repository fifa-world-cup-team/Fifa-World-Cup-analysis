"use client";

import { useEffect, useState } from "react";
import { MatchesSection } from "@/components/MatchesSection";
import { ErrorState, LoadingState } from "@/components/PageState";
import { fetchMatches, type Match } from "@/lib/api";

const REFRESH_INTERVAL_MS = 60_000;

export function MatchesPageClient() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchMatches();
        if (cancelled) return;
        setMatches(data);
        setError(null);
        setLastUpdated(new Date());
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Erreur inconnue.");
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

  if (loading) return <LoadingState label="Chargement des matchs..." />;
  if (error) return <ErrorState message={error} />;

  return (
    <>
      {lastUpdated && (
        <p className="text-sm text-emerald-200/60">
          Derniere mise a jour : {lastUpdated.toLocaleTimeString("fr-FR")}
        </p>
      )}
      <MatchesSection matches={matches} />
    </>
  );
}
