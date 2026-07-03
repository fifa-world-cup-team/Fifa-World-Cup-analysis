"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Accueil" },
  { href: "/matches", label: "Matchs" },
  { href: "/standings", label: "Classements" },
  { href: "/tournament", label: "Tournoi" },
  { href: "/predict", label: "Predicteur" },
];

export function DashboardShell({
  children,
  subtitle,
}: {
  children: React.ReactNode;
  subtitle?: string;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#0d3b2a,_#06120c_60%)] pb-20 font-sans">
      <header className="border-b border-emerald-900/40 bg-gradient-to-r from-emerald-950 via-emerald-900 to-emerald-950">
        <div className="mx-auto flex max-w-6xl flex-col gap-5 px-4 py-7">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Link href="/" className="flex items-center gap-3">
              <span className="text-4xl" aria-hidden="true">
                WC
              </span>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                  World Cup Predictor <span className="text-emerald-400">2026</span>
                </h1>
                <p className="text-sm text-emerald-200/80">
                  {subtitle ?? "Predictions, classements et simulation du tournoi."}
                </p>
              </div>
            </Link>
          </div>

          <nav className="flex gap-2 overflow-x-auto pb-1" aria-label="Navigation principale">
            {NAV_ITEMS.map((item) => {
              const active =
                item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    active
                      ? "rounded-full bg-emerald-400 px-4 py-2 text-sm font-semibold text-emerald-950"
                      : "rounded-full bg-emerald-950/60 px-4 py-2 text-sm font-semibold text-emerald-100 ring-1 ring-emerald-700/40 transition-colors hover:bg-emerald-900"
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 pt-8">{children}</main>
    </div>
  );
}
