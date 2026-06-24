# Team Tasks

Ce fichier sert a repartir le travail sans commencer trop complexe.

## Personne 1 - Data / ML

Objectif: preparer la partie donnees et modele.

Taches futures:

- trouver les sources de donnees football
- recuperer les matchs et resultats
- ajouter un dataset Elo
- creer les premieres features
- entrainer un modele simple `home_win`, `draw`, `away_win`
- configurer DVC
- logger les runs dans MLflow

Branche conseillee:

```text
feature/ml-model
```

## Personne 2 - Backend / API

Objectif: creer l'API qui servira les predictions.

Taches futures:

- creer un backend FastAPI
- ajouter un endpoint `/health`
- ajouter un endpoint `/predict`
- charger le modele depuis MLflow
- connecter Supabase pour stocker predictions et resultats reels
- exposer les metriques `/metrics`

Branche conseillee:

```text
feature/backend-api
```

## Personne 3 - Frontend / DevOps

Objectif: preparer l'interface et le deploiement.

Taches futures:

- creer un frontend Next.js
- afficher un formulaire de selection d'equipes
- afficher les probabilites de prediction
- preparer Docker
- preparer GitHub Actions
- preparer Render
- preparer Prometheus et Grafana

Branche conseillee:

```text
feature/frontend-devops
```

## Regle commune

Chaque personne travaille dans sa branche `feature/*`, puis ouvre une Pull
Request vers `dev`.
