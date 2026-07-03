export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "https://fifa-backend-production.onrender.com";

export type Team = { name: string; crest: string | null } | null;

export type Match = {
  id: number;
  utc_date: string;
  status: string;
  stage: string;
  group: string | null;
  matchday: number | null;
  home_team: Team;
  away_team: Team;
  home_score: number | null;
  away_score: number | null;
};

export type StandingRow = {
  position: number;
  team: string;
  crest: string | null;
  played: number;
  won: number;
  draw: number;
  lost: number;
  points: number;
  goal_difference: number;
};

export type GroupStanding = {
  group: string;
  table: StandingRow[];
};

export type Prediction = {
  prediction: string;
  probabilities: Record<string, number>;
};

export type TournamentMatch = {
  match_number?: number;
  home_team: string | null;
  away_team: string | null;
  resolved: boolean;
  source?: "actual_result" | "predicted";
  winner: string | null;
  home_score?: number;
  away_score?: number;
  probabilities?: Record<string, number>;
};

export type TournamentRound = {
  stage: string;
  matches: TournamentMatch[];
};

export type TournamentResult = {
  rounds: TournamentRound[];
  champion: string | null;
};

export const STAGE_LABELS: Record<string, string> = {
  GROUP_STAGE: "Phase de groupes",
  LAST_32: "32èmes de finale",
  LAST_16: "8èmes de finale",
  ROUND_OF_16: "8èmes de finale",
  QUARTER_FINALS: "Quarts de finale",
  SEMI_FINALS: "Demi-finales",
  THIRD_PLACE: "Petite finale",
  FINAL: "Finale",
};

// "home"/"away" only reflect football-data.org's listing order for a given
// fixture, not a real home-advantage (World Cup matches are on neutral
// ground). Always resolve these labels to the actual team names in the UI.
export function resultLabel(result: string, homeTeam: string, awayTeam: string): string {
  if (result === "home_win") return `Victoire ${homeTeam}`;
  if (result === "away_win") return `Victoire ${awayTeam}`;
  return "Match nul";
}

export function probabilityLabels(
  probabilities: Record<string, number>,
  homeTeam: string,
  awayTeam: string,
): { label: string; value: number }[] {
  return Object.entries(probabilities).map(([result, value]) => ({
    label: resultLabel(result, homeTeam, awayTeam),
    value,
  }));
}

export async function fetchMatches(): Promise<Match[]> {
  const response = await fetch(`${API_URL}/matches`);
  if (!response.ok) {
    throw new Error("Impossible de récupérer les matchs.");
  }
  return response.json();
}

export async function fetchStandings(): Promise<GroupStanding[]> {
  const response = await fetch(`${API_URL}/standings`);
  if (!response.ok) {
    throw new Error("Impossible de récupérer les classements.");
  }
  return response.json();
}

export async function fetchTournament(): Promise<TournamentResult> {
  const response = await fetch(`${API_URL}/tournament`);
  if (!response.ok) {
    throw new Error("Impossible de simuler le tournoi.");
  }
  return response.json();
}

export async function fetchPrediction(
  homeTeam: string,
  awayTeam: string,
  stage: string,
): Promise<Prediction> {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      home_team: homeTeam,
      away_team: awayTeam,
      stage,
    }),
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail ?? "La prédiction a échoué.");
  }
  return body;
}
