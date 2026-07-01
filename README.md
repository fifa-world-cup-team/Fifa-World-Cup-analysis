# World Cup Predictor 2026

Projet MLOps simple autour de la Coupe du Monde 2026.

L'objectif est de construire progressivement une application web capable de
predire le resultat d'un match de football entre deux equipes.

## Idee du projet

L'utilisateur choisit deux equipes, par exemple:

```text
France vs Argentina
```

L'application devra retourner:

- probabilite de victoire de l'equipe a domicile
- probabilite de match nul
- probabilite de victoire de l'equipe exterieure
- score probable
- plus tard, simulation du tournoi

## Objectif Machine Learning

Pour commencer simplement, le modele sera un probleme de classification a 3
classes:

- `home_win`
- `draw`
- `away_win`

Les premieres features prevues:

- rating Elo des equipes
- forme recente
- confrontations directes
- buts marques et encaisses en moyenne

Le score exact et la simulation du tournoi seront derives plus tard a partir des
probabilites du meme modele.

## Stack prevue

- Backend: FastAPI
- Frontend: Next.js
- Data versioning: DVC
- Model tracking et registry: MLflow avec DagsHub
- Database: Supabase Postgres
- Monitoring: Prometheus et Grafana
- Deployment: Render
- CI/CD: GitHub Actions

## Strategie Git

Le projet doit respecter ce modele de branches:

```text
feature/* -> dev -> staging -> main
```

- `feature/*`: developpement de chaque membre
- `dev`: integration du travail de l'equipe
- `staging`: validation pre-production
- `main`: production

Personne ne travaille directement sur `dev`, `staging` ou `main`.

## Repartition initiale

- Data / ML: donnees, features, modele, DVC, MLflow
- Backend / API: FastAPI, endpoints, connexion au modele et a Supabase
- Frontend / DevOps: interface Next.js, Docker, CI/CD, Render, monitoring

Voir le fichier `docs/team-tasks.md` pour plus de details.

## Mise a jour des donnees

Les donnees brutes ne se mettent pas a jour automatiquement.

Pour actualiser les matchs depuis l'API puis regenerer le fichier traite:

```powershell
python scripts/update_data.py
```

Cette commande cree localement:

```text
data/raw/worldcup_matches.json
data/processed/matches_processed.csv
```

Ces fichiers generes sont ignores par Git pour le moment. Ils seront versionnes
plus tard avec DVC.

## Classement FIFA

Le projet peut aussi recuperer le classement FIFA depuis l'API World Football
Ranking de RapidAPI. Cette source servira plus tard a ajouter des features comme
le rang FIFA, les points FIFA et la difference de niveau entre deux equipes.

Ajouter la cle RapidAPI dans `.env`:

```text
WORLD_FOOTBALL_RANKING_API_KEY=your_key_here
```

Puis lancer:

```powershell
python scripts/ingest_fifa_rankings.py
```

Cette commande cree localement:

```text
data/raw/fifa_ranking_current.json
```

Si RapidAPI retourne une erreur `401` ou `403`, verifier que la cle est correcte
et que l'API World Football Ranking est bien activee dans le compte RapidAPI.
