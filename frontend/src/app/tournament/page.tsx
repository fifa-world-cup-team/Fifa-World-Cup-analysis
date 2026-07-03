import { DashboardShell } from "@/components/DashboardShell";
import { TournamentSection } from "@/components/TournamentSection";

export const dynamic = "force-dynamic";

export default function TournamentPage() {
  return (
    <DashboardShell subtitle="Simulation du bracket et champion probable.">
      <TournamentSection />
    </DashboardShell>
  );
}
