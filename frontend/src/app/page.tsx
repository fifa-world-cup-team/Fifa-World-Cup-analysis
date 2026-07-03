import Link from "next/link";
import { DashboardShell } from "@/components/DashboardShell";

// This dashboard is entirely client-fetched and updates on its own every
// 60s. Without this, Next.js treats it as static content and tells CDNs to
// cache the HTML for up to a year, which serves a stale page after every
// deploy until that cache is manually purged.
export const dynamic = "force-dynamic";

const CARDS = [
  {
    href: "/matches",
    title: "Matchs",
    description: "Voir le calendrier, les prochains matchs et les derniers resultats.",
  },
  {
    href: "/standings",
    title: "Classements",
    description: "Consulter les groupes, points, matchs joues et differences de buts.",
  },
  {
    href: "/tournament",
    title: "Tournoi",
    description: "Simuler le bracket et afficher le vainqueur final probable.",
  },
  {
    href: "/predict",
    title: "Predicteur",
    description: "Choisir deux equipes et obtenir les probabilites du modele.",
  },
];

export default function Page() {
  return (
    <DashboardShell subtitle="Choisis une page pour explorer le projet.">
      <section className="grid gap-4 sm:grid-cols-2">
        {CARDS.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6 shadow-lg shadow-black/20 ring-1 ring-transparent transition hover:border-emerald-500/60 hover:ring-emerald-500/30"
          >
            <h2 className="text-xl font-bold text-emerald-50">{card.title}</h2>
            <p className="mt-2 text-sm leading-6 text-emerald-100/65">{card.description}</p>
          </Link>
        ))}
      </section>
    </DashboardShell>
  );
}
