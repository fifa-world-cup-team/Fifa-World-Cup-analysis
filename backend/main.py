import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.model_service import PredictionError, load_model, load_rankings, predict_match

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


class MatchRequest(BaseModel):
    home_team: str
    away_team: str
    stage: str = "GROUP_STAGE"


@app.get("/health")
def health() -> dict:
    model_loaded = app_state.get("model") is not None
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_uri": app_state.get("model_uri"),
        "detail": None if model_loaded else app_state.get("error"),
    }


@app.post("/predict")
def predict(request: MatchRequest) -> dict:
    if app_state.get("model") is None or app_state.get("rankings") is None:
        raise HTTPException(
            status_code=503,
            detail=app_state.get("error") or "Model not loaded",
        )

    try:
        return predict_match(
            app_state["model"],
            app_state["rankings"],
            request.home_team,
            request.away_team,
            request.stage,
        )
    except PredictionError as error:
        raise HTTPException(status_code=422, detail=str(error))
