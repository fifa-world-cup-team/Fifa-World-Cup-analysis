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
| feature/mlflow-integration | Tracking MLflow dans le script d'entraînement | Diaby |
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

### 1. Versionner le nouveau dataset avec DVC
Ajouter `data/processed/training_matches.csv` à DVC après validation de la PR.

### 2. GitHub Actions CI/CD
PR → dev fait (tests). Reste : build Docker (bloqué par l'absence de backend), tests d'intégration et e2e, pipelines dev → staging et staging → main.
### 3. Backend FastAPI + Docker
### 4. Monitoring Prometheus + Grafana
### 5. Frontend Next.js
### 6. Déploiement cloud
### 7. README final
