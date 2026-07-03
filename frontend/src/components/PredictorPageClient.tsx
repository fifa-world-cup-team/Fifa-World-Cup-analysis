"use client";

import { useEffect, useState } from "react";
import { ErrorState, LoadingState } from "@/components/PageState";
import { PredictorForm } from "@/components/PredictorForm";
import { fetchStandings, type GroupStanding } from "@/lib/api";

export function PredictorPageClient() {
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
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) return <LoadingState label="Chargement des equipes..." />;
  if (error) return <ErrorState message={error} />;

  return <PredictorForm groups={groups} />;
}
