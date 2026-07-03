import { DashboardShell } from "@/components/DashboardShell";
import { StandingsPageClient } from "@/components/StandingsPageClient";

export const dynamic = "force-dynamic";

export default function StandingsPage() {
  return (
    <DashboardShell subtitle="Classements des groupes de la Coupe du Monde.">
      <StandingsPageClient />
    </DashboardShell>
  );
}
