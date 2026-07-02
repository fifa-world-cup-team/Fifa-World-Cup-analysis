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
      <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Prochains matchs & prédictions
        </h2>
        {groupByStage(upcoming).map(([stage, stageMatches]) => (
          <div key={stage} className="mb-4">
            <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-400">
              {STAGE_LABELS[stage] ?? stage}
            </h3>
            {stageMatches.map((match) => (
              <MatchRow key={match.id} match={match} />
            ))}
          </div>
        ))}
        {upcoming.length === 0 && (
          <p className="text-sm text-zinc-500">Aucun match à venir pour le moment.</p>
        )}
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Derniers résultats
        </h2>
        {finished.map((match) => (
          <MatchRow key={match.id} match={match} />
        ))}
        {finished.length === 0 && (
          <p className="text-sm text-zinc-500">Aucun résultat pour le moment.</p>
        )}
      </section>
    </div>
  );
}
