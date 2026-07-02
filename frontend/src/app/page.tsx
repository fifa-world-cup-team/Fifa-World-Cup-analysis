import { HomeClient } from "@/components/HomeClient";

// This dashboard is entirely client-fetched and updates on its own every
// 60s. Without this, Next.js treats it as static content and tells CDNs to
// cache the HTML for up to a year, which serves a stale page after every
// deploy until that cache is manually purged.
export const dynamic = "force-dynamic";

export default function Page() {
  return <HomeClient />;
}
