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

### 2. ~~GitHub Actions CI/CD~~ (fait)
Les 3 pipelines exigés tournent réellement : PR → dev (tests + build Docker), dev → staging (tests, dvc pull, entraînement candidat, quality gate accuracy >= 0.5, promotion Staging/Production MLflow, déploiement Render), staging → main (vérification du gate + déploiement Render prod). Testés en conditions réelles le 2026-07-02, prédiction confirmée sur les deux environnements.
### 3. ~~Backend FastAPI + Docker~~ (fait)
API FastAPI (`backend/`) qui charge le modèle depuis le MLflow Model Registry (stage configurable via `MODEL_STAGE`), sert `/health` + `POST /predict`. Le conteneur récupère les données via `dvc pull` à son démarrage (identifiants DagsHub passés en variables d'env).
### 4. ~~Déploiement cloud~~ (fait, Render)
- Staging : https://fifa-world-cup-analysis-phep.onrender.com
- Production : https://fifa-backend-production.onrender.com
### 5. Monitoring Prometheus + Grafana
### 6. Frontend Next.js
### 7. README final (architecture, CI/CD, promotion, reproductibilité)
