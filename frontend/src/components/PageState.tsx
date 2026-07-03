export function LoadingState({ label = "Chargement..." }: { label?: string }) {
  return (
    <p className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 px-5 py-4 text-sm text-emerald-100/70">
      {label}
    </p>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <p className="rounded-2xl bg-red-950/60 px-5 py-4 text-sm text-red-200 ring-1 ring-red-800">
      {message}
    </p>
  );
}
