# Suivi projet MLOps - FIFA World Cup 2026

Groupe : Diaby - Adrien - Ilyesse
Repo GitHub : https://github.com/Adrienqry/Fifa-World-Cup-analysis
Repo DagsHub : https://dagshub.com/Adrienqry/Fifa-World-Cup-analysis

---

## Ce qui est fait ?

| Branche | Ce que ca fait | Qui |
|---|---|---|
| feature/fix-gitignore | Fix du .gitignore qui bloquait git add | Diaby |
| feature/strengthen-tests | 4 tests solides + pytest.ini | Diaby |
| feature/mlflow-integration | Tracking MLflow dans le script d'entrainement | Diaby |
| feature/dvc-setup | Versioning des donnees avec DVC + stockage DagsHub | Diaby |
| feature/baseline-model | Script d'entrainement du modele (LogisticRegression) | Adrien |
| feature/data-tests | Tests basiques preprocessing + train | Ilyesse |
| feature/fifa-ranking-api | Ingestion du classement FIFA via RapidAPI pour enrichir les features | Adrien |

---

## Verifications

| Element | Statut |
|---|---|
| RapidAPI World Football Ranking | OK - appel live valide |
| Fichier genere | `data/raw/fifa_ranking_current.json` |
| Donnees recuperees | 211 equipes, classement officiel du 11 June, 2026 |
| Dataset ML ranking | `data/processed/fifa_rankings_current.csv` |
| Dataset d'entrainement enrichi | `data/processed/training_matches.csv` |
| Git | Le JSON genere est ignore par Git |
| Tests | 13 tests passent |
| Modele baseline enrichi | Accuracy locale: 0.643 |

---

## Ce qui reste a faire ?

### 1. Versionner le nouveau dataset avec DVC
Ajouter `data/processed/training_matches.csv` a DVC apres validation de la PR.

### 2. GitHub Actions CI/CD
### 3. Backend FastAPI + Docker
### 4. Monitoring Prometheus + Grafana
### 5. Frontend Next.js
### 6. Deploiement cloud
### 7. README final
