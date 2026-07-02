import { STAGE_LABELS, type Match } from "@/lib/api";
import { MatchRow } from "./MatchRow";

const STAGE_ORDER = [
  "GROUP_STAGE",
  "LAST_32",
  "LAST_16",
  "ROUND_OF_16",
  "QUARTER_FINALS",
  "SEMI_FINALS",
  "THIRD_PLACE",
  "FINAL",
];

function groupByStage(matches: Match[]): [string, Match[]][] {
  const groups = new Map<string, Match[]>();
  for (const match of matches) {
    const key = match.stage;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(match);
  }
  return STAGE_ORDER.filter((stage) => groups.has(stage)).map((stage) => [
    stage,
    groups.get(stage)!,
  ]);
}

export function MatchesSection({ matches }: { matches: Match[] }) {
  const upcoming = matches
    .filter((m) => m.status !== "FINISHED")
    .sort((a, b) => a.utc_date.localeCompare(b.utc_date));

  const finished = matches
    .filter((m) => m.status === "FINISHED")
    .sort((a, b) => b.utc_date.localeCompare(a.utc_date))
    .slice(0, 20);

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-5 shadow-lg shadow-black/20 backdrop-blur-sm">
        <h2 className="mb-2 flex items-center gap-2 text-lg font-semibold text-emerald-50">
          📅 Prochains matchs & prédictions
        </h2>
        {groupByStage(upcoming).map(([stage, stageMatches]) => (
          <div key={stage} className="mb-3">
            <h3 className="mb-1 mt-3 text-xs font-bold uppercase tracking-widest text-emerald-400/70">
              {STAGE_LABELS[stage] ?? stage}
            </h3>
            <div className="divide-y divide-emerald-900/40">
              {stageMatches.map((match) => (
                <MatchRow key={match.id} match={match} />
              ))}
            </div>
          </div>
        ))}
        {upcoming.length === 0 && (
          <p className="text-sm text-emerald-200/60">Aucun match à venir pour le moment.</p>
        )}
      </section>

      <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-5 shadow-lg shadow-black/20 backdrop-blur-sm">
        <h2 className="mb-2 flex items-center gap-2 text-lg font-semibold text-emerald-50">
          ⚽ Derniers résultats
        </h2>
        <div className="divide-y divide-emerald-900/40">
          {finished.map((match) => (
            <MatchRow key={match.id} match={match} />
          ))}
        </div>
        {finished.length === 0 && (
          <p className="text-sm text-emerald-200/60">Aucun résultat pour le moment.</p>
        )}
      </section>
    </div>
  );
}
