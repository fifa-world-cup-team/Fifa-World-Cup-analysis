import { DashboardShell } from "@/components/DashboardShell";
import { MatchesPageClient } from "@/components/MatchesPageClient";

export const dynamic = "force-dynamic";

export default function MatchesPage() {
  return (
    <DashboardShell subtitle="Calendrier, resultats et predictions par match.">
      <MatchesPageClient />
    </DashboardShell>
  );
}
