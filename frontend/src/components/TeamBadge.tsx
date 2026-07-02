import type { Team } from "@/lib/api";

export function TeamBadge({ team, align = "left" }: { team: Team; align?: "left" | "right" }) {
  const name = team?.name ?? "À déterminer";

  return (
    <span
      className={`flex items-center gap-2 ${align === "right" ? "flex-row-reverse text-right" : "text-left"}`}
    >
      {team?.crest ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={team.crest} alt={name} className="h-5 w-5 object-contain" />
      ) : (
        <span className="h-5 w-5 rounded-full bg-zinc-200 dark:bg-zinc-700" />
      )}
      <span className={team ? "" : "italic text-zinc-400 dark:text-zinc-500"}>{name}</span>
    </span>
  );
}
