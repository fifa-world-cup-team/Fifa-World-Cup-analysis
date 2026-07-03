import { DashboardShell } from "@/components/DashboardShell";
import { PredictorPageClient } from "@/components/PredictorPageClient";

export const dynamic = "force-dynamic";

export default function PredictPage() {
  return (
    <DashboardShell subtitle="Selectionne deux equipes et lance une prediction.">
      <PredictorPageClient />
    </DashboardShell>
  );
}
