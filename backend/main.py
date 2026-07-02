import logging
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST

from backend import football_data, metrics
from backend.model_service import PredictionError, load_model, load_rankings, predict_match
from backend.tournament import simulate_knockout_stages

logger = logging.getLogger("backend")

app_state: dict = {"model": None, "model_uri": None, "rankings": None, "error": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app_state["model"], app_state["model_uri"] = load_model()
    except PredictionError as error:
        logger.warning("Model not loaded at startup: %s", error)
        app_state["error"] = str(error)

    try:
        app_state["rankings"] = load_rankings()
    except PredictionError as error:
        logger.warning("Rankings not loaded at startup: %s", error)
        app_state["error"] = str(error)

    yield


app = FastAPI(title="FIFA World Cup Prediction API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    stage: str = "GROUP_STAGE"


@app.get("/health")
def health() -> dict:
    model_loaded = app_state.get("model") is not None and app_state.get("rankings") is not None
    metrics.set_backend_healthy(model_loaded)
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_uri": app_state.get("model_uri"),
        "detail": None if model_loaded else app_state.get("error"),
    }


@app.get("/metrics")
def metrics_endpoint() -> Response:
    model_loaded = app_state.get("model") is not None and app_state.get("rankings") is not None
    metrics.set_backend_healthy(model_loaded)
    return Response(metrics.render_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/matches")
def matches() -> list[dict]:
    try:
        return football_data.get_matches()
    except (RuntimeError, requests.RequestException) as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/standings")
def standings() -> list[dict]:
    try:
        return football_data.get_standings()
    except (RuntimeError, requests.RequestException) as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/tournament")
def tournament() -> dict:
    if app_state.get("model") is None or app_state.get("rankings") is None:
        raise HTTPException(
            status_code=503,
            detail=app_state.get("error") or "Model not loaded",
        )

    try:
        all_matches = football_data.get_matches()
    except (RuntimeError, requests.RequestException) as error:
        raise HTTPException(status_code=502, detail=str(error))

    return simulate_knockout_stages(app_state["model"], app_state["rankings"], all_matches)


@app.post("/predict")
def predict(request: MatchRequest) -> dict:
    metrics.PREDICTION_REQUESTS_TOTAL.inc()

    if app_state.get("model") is None or app_state.get("rankings") is None:
        metrics.PREDICTION_FAILURES_TOTAL.inc()
        raise HTTPException(
            status_code=503,
            detail=app_state.get("error") or "Model not loaded",
        )

    try:
        with metrics.PREDICTION_LATENCY_SECONDS.time():
            return predict_match(
                app_state["model"],
                app_state["rankings"],
                request.home_team,
                request.away_team,
                request.stage,
            )
    except PredictionError as error:
        metrics.PREDICTION_FAILURES_TOTAL.inc()
        raise HTTPException(status_code=422, detail=str(error))
