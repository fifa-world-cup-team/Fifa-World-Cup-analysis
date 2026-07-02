import type { Team } from "@/lib/api";

export function TeamBadge({
  team,
  align = "left",
  size = "md",
}: {
  team: Team;
  align?: "left" | "right";
  size?: "sm" | "md";
}) {
  const name = team?.name ?? "À déterminer";
  const crestSize = size === "sm" ? "h-4 w-4" : "h-6 w-6";

  return (
    <span
      className={`flex items-center gap-2 ${align === "right" ? "flex-row-reverse text-right" : "text-left"}`}
    >
      {team?.crest ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={team.crest} alt={name} className={`${crestSize} shrink-0 object-contain drop-shadow-sm`} />
      ) : (
        <span className={`${crestSize} shrink-0 rounded-full bg-emerald-900/60 ring-1 ring-emerald-700/50`} />
      )}
      <span className={team ? "font-medium text-emerald-50" : "italic text-emerald-100/40"}>
        {name}
      </span>
    </span>
  );
}
