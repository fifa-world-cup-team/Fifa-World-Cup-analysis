import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

PREDICTION_REQUESTS_TOTAL = Counter(
    "prediction_requests_total",
    "Total number of prediction requests received",
)
PREDICTION_FAILURES_TOTAL = Counter(
    "prediction_failures_total",
    "Total number of prediction requests that failed",
)
PREDICTION_LATENCY_SECONDS = Histogram(
    "prediction_latency_seconds",
    "Time spent serving a prediction request, in seconds",
)
BACKEND_HEALTHY = Gauge(
    "backend_healthy",
    "Whether the backend has a model and rankings loaded (1) or not (0)",
)
BACKEND_UPTIME_SECONDS = Gauge(
    "backend_uptime_seconds",
    "Seconds since the backend process started",
)

_START_TIME = time.time()


def set_backend_healthy(is_healthy: bool) -> None:
    BACKEND_HEALTHY.set(1 if is_healthy else 0)


def render_latest() -> bytes:
    BACKEND_UPTIME_SECONDS.set(time.time() - _START_TIME)
    return generate_latest()
