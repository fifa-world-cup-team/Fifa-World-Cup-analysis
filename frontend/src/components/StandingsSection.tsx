import type { GroupStanding } from "@/lib/api";

export function StandingsSection({ groups }: { groups: GroupStanding[] }) {
  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        Classements par groupe
      </h2>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <div key={group.group}>
            <h3 className="mb-2 text-sm font-semibold text-zinc-700 dark:text-zinc-300">
              {group.group}
            </h3>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-zinc-400">
                  <th className="pb-1">Équipe</th>
                  <th className="pb-1 text-center">MJ</th>
                  <th className="pb-1 text-center">Pts</th>
                  <th className="pb-1 text-center">+/-</th>
                </tr>
              </thead>
              <tbody>
                {group.table.map((row) => (
                  <tr
                    key={row.team}
                    className="border-t border-zinc-100 text-zinc-700 dark:border-zinc-800 dark:text-zinc-300"
                  >
                    <td className="flex items-center gap-1.5 py-1">
                      {row.crest ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={row.crest} alt={row.team} className="h-4 w-4 object-contain" />
                      ) : null}
                      {row.team}
                    </td>
                    <td className="text-center">{row.played}</td>
                    <td className="text-center font-semibold">{row.points}</td>
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
