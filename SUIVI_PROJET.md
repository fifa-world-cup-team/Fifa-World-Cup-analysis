# Suivi projet MLOps – FIFA World Cup 2026

Groupe : Diaby – Adrien – Ilyesse
Repo GitHub : https://github.com/Adrienqry/Fifa-World-Cup-analysis
Repo DagsHub : https://dagshub.com/Adrienqry/Fifa-World-Cup-analysis

---

## Ce qui est fait ?

| Branche | Ce que ça fait | Qui |
|---|---|---|
| feature/fix-gitignore | Fix du .gitignore qui bloquait git add | Diaby |
| feature/strengthen-tests | 4 tests solides + pytest.ini | Diaby |
| feature/mlflow-integration | Ajout de la dépendance mlflow (tracking pas encore implémenté à ce stade) | Diaby |
| feature/mlflow-tracking-real | Vrai tracking MLflow (run, params, métriques, registry) + traçabilité commit Git/version DVC, testé en direct sur DagsHub | Diaby |
| feature/dvc-setup | Versioning des données avec DVC + stockage DagsHub | Diaby |
| feature/baseline-model | Script d'entraînement du modèle (LogisticRegression) | Adrien |
| feature/data-tests | Tests basiques preprocessing + train | Ilyesse |
| feature/fifa-ranking-api | Ingestion du classement FIFA via RapidAPI pour enrichir les features | Adrien |
| feature/project-tracking | Workflow GitHub Actions CI (tests pytest sur PR vers dev) | Diaby |

---

## Vérifications

| Élément | Statut |
|---|---|
| RapidAPI World Football Ranking | OK - appel live validé |
| Fichier généré | `data/raw/fifa_ranking_current.json` |
| Données récupérées | 211 équipes, classement officiel du 11 June, 2026 |
| Dataset ML ranking | `data/processed/fifa_rankings_current.csv` |
| Dataset d'entraînement enrichi | `data/processed/training_matches.csv` |
| Git | Le JSON généré est ignoré par Git |
| Tests | 13 tests passent |
| Modèle baseline enrichi | Accuracy locale: 0.643 |

---

## Ce qui reste à faire ?

### 1. ~~Versionner le nouveau dataset avec DVC~~ (fait)
`fifa_ranking_current.json`, `fifa_rankings_current.csv` et `training_matches.csv` trackés avec DVC et poussés sur DagsHub.

### 2. GitHub Actions CI/CD
PR → dev fait (tests dont 2 intégration + 1 e2e, build Docker). Pipelines dev → staging (tests, dvc pull, entraînement candidat, quality gate accuracy >= 0.5, promotion Staging/Production, déploiement Render) et staging → main (vérification gate + déploiement Render prod) écrits. Reste : ajouter les secrets GitHub (DAGSHUB_USERNAME, DAGSHUB_TOKEN, MLFLOW_TRACKING_URI, RENDER_STAGING_DEPLOY_HOOK, RENDER_PRODUCTION_DEPLOY_HOOK) et tester en conditions réelles.
### 3. ~~Backend FastAPI + Docker~~ (fait)
API FastAPI (`backend/`) qui charge le modèle depuis le MLflow Model Registry (stage configurable via `MODEL_STAGE`, défaut `None`), et sert `/health` + `POST /predict` (home_team, away_team, stage -> prédiction + probabilités). `Dockerfile` ajouté, build vérifié en local et intégré au CI (PR -> dev, sans push). Note : l'image ne contient pas encore les données DVC (`data/`) — à prévoir au déploiement (pipeline dev -> staging).
### 4. Monitoring Prometheus + Grafana
### 5. Frontend Next.js
### 6. Déploiement cloud
### 7. README final
