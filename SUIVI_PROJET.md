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
| feature/docker-backend | Dockerfile backend + build Docker en CI | Diaby |
| feature/model-promotion-pipeline | Pipeline de promotion (candidat -> Staging -> Production, quality gate) | Diaby |
| feature/docker-dvc-pull | Le conteneur récupère les données via DVC à son démarrage | Diaby |
| feature/backend-api | Backend FastAPI qui sert les prédictions depuis le registry MLflow | Diaby |
| feature/prometheus-metrics | Endpoint `/metrics` | Diaby |
| feature/prometheus-grafana | Déploiement Prometheus + Grafana | Diaby |
| feature/readme-final | README final + premier frontend Next.js | Diaby |
| fix/cors | Fix CORS (le frontend ne pouvait pas du tout appeler l'API) | Diaby |
| feature/live-matches-standings | Reconstruction du frontend en vrai dashboard (matchs live, classements, simulation du vainqueur) | Diaby |
| fix/ui-team-names-and-refresh | Fix noms d'équipes (plus de "domicile/extérieur") + refonte visuelle complète | Diaby |
| fix/disable-static-cache | Fix cache CDN d'1 an qui servait une page périmée sur Render | Diaby |

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
| Tests | 38 tests passent (unit + intégration + e2e + tournoi + football_data) |
| Modèle baseline enrichi | Accuracy locale: 0.643 (dernier run staging: 0.579, versionné dans MLflow) |

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
### 5. ~~Monitoring Prometheus + Grafana~~ (fait)
Endpoint `/metrics` sur le backend, déployés sur Render : Prometheus (https://fifa-prometheus.onrender.com, scrape la prod toutes les 30s) et Grafana (https://fifa-graphana.onrender.com, dashboard "FIFA World Cup Backend" provisionné automatiquement). Chaîne vérifiée en direct.
### 6. ~~Frontend Next.js~~ (v2, vrai dashboard)
Le premier frontend (simple formulaire) était trop pauvre par rapport à ce que l'équipe voulait. Reconstruit en vrai dashboard :
- `GET /matches` et `GET /standings` (backend) : proxy en cache (60s) de l'API football-data.org, vraies données de la Coupe du Monde 2026 en cours (104 matchs, 12 groupes)
- Frontend : tableau des matchs à venir avec prédiction par match (bouton), derniers résultats, classements par groupe avec écussons, + simulateur libre (2 équipes au choix, sans label "domicile/extérieur" ni "équipe 1/2" — juste les vrais noms/écussons)
- Rafraîchissement automatique toutes les 60s (matchs, classements, et simulation du vainqueur)
- `GET /tournament` (backend) : simule tout le bracket à élimination directe (32èmes -> finale) avec notre modèle pour les tours pas encore joués, et les vrais résultats pour ceux déjà joués. Les cases encore "à déterminer" côté API sont remplies en enchaînant les vainqueurs/perdants dans l'ordre chronologique (approximation assumée et affichée, pas un vrai tirage FIFA). Retourne un vainqueur final prédit. Testé (y compris un test qui reproduit un bug trouvé : une équipe réutilisée deux fois dans le même tour, corrigé).
- Refonte visuelle complète (thème sombre "terrain de foot", badges de statut, écussons, carte vainqueur)
- Fix CORS (le premier frontend déployé ne pouvait pas du tout appeler l'API, bloqué silencieusement par le navigateur)
- Fix cache CDN (Next.js gardait la page en cache 1 an sur Render après chaque déploiement)

**Point ouvert** : le rendu visuel final (une fois JS exécuté dans un vrai navigateur) n'a pas pu être vérifié par l'assistant — pas d'accès navigateur, seulement `curl` (qui ne voit que le squelette HTML de chargement, le contenu réel est injecté par React côté client). À valider par l'équipe directement sur https://fifa-frontend-7be5.onrender.com
### 7. ~~README final~~ (fait)
Architecture, CI/CD, promotion, reproductibilité, monitoring, tous les liens de déploiement.

---

## Projet complet
Toutes les exigences du cahier des charges sont couvertes : branching model, 3 pipelines CI/CD (testés en conditions réelles), tests (unit/intégration/e2e), DVC, MLflow (tracking + registry + promotion), backend Dockerisé, monitoring Prometheus/Grafana, frontend (dashboard temps réel avec matchs/classements/prédictions/simulation du vainqueur), déploiement cloud, README.

Reste : présentation en classe, + valider visuellement le rendu final du frontend (point ouvert ci-dessus).
