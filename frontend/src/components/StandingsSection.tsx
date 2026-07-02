import type { GroupStanding } from "@/lib/api";

export function StandingsSection({ groups }: { groups: GroupStanding[] }) {
  return (
    <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-5 shadow-lg shadow-black/20 backdrop-blur-sm">
      <h2 className="mb-1 flex items-center gap-2 text-lg font-semibold text-emerald-50">
        📊 Classements par groupe
      </h2>
      <p className="mb-4 text-xs text-emerald-200/50">
        Les 2 premières places de chaque groupe (surlignées) sont qualifiées directement.
      </p>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <div key={group.group} className="rounded-xl bg-emerald-950/50 p-3 ring-1 ring-emerald-900/50">
            <h3 className="mb-2 text-sm font-bold uppercase tracking-wide text-emerald-300">
              {group.group}
            </h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-emerald-400/50">
                  <th className="pb-1 font-medium">Équipe</th>
                  <th className="pb-1 text-center font-medium">MJ</th>
                  <th className="pb-1 text-center font-medium">Pts</th>
                  <th className="pb-1 text-center font-medium">+/-</th>
                </tr>
              </thead>
              <tbody>
                {group.table.map((row) => (
                  <tr
                    key={row.team}
                    className={
                      row.position <= 2
                        ? "bg-emerald-500/10 text-emerald-50"
                        : "text-emerald-100/60"
                    }
                  >
                    <td className="flex items-center gap-1.5 py-1.5 pl-1.5">
                      {row.crest ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={row.crest} alt={row.team} className="h-4 w-4 object-contain" />
                      ) : null}
                      <span className={row.position <= 2 ? "font-semibold" : ""}>{row.team}</span>
                    </td>
                    <td className="text-center">{row.played}</td>
                    <td className="text-center font-bold">{row.points}</td>
                    <td className="text-center">{row.goal_difference}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </section>
  );
}
