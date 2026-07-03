"use client";

import { useEffect, useState } from "react";
import { ErrorState, LoadingState } from "@/components/PageState";
import { StandingsSection } from "@/components/StandingsSection";
import { fetchStandings, type GroupStanding } from "@/lib/api";

const REFRESH_INTERVAL_MS = 60_000;

export function StandingsPageClient() {
  const [groups, setGroups] = useState<GroupStanding[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchStandings();
        if (cancelled) return;
        setGroups(data);
        setError(null);
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

  if (loading) return <LoadingState label="Chargement des classements..." />;
  if (error) return <ErrorState message={error} />;

  return <StandingsSection groups={groups} />;
}
