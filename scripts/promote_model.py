import os
import sys

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.metrics import accuracy_score
from mlflow.tracking import MlflowClient

from scripts.train_baseline_model import (
    DATASET_PATH,
    FEATURE_COLUMNS,
    REGISTERED_MODEL_NAME,
    TARGET_COLUMN,
    load_dataset,
    load_env_file,
)

QUALITY_GATE_MIN_ACCURACY = float(os.getenv("QUALITY_GATE_MIN_ACCURACY", "0.5"))
BACKTEST_MATCH_COUNT = int(os.getenv("QUALITY_GATE_BACKTEST_MATCH_COUNT", "10"))
BACKTEST_MIN_IMPROVEMENT = float(os.getenv("QUALITY_GATE_MIN_IMPROVEMENT", "0.0"))


def get_latest_candidate_version(client: MlflowClient, model_name: str):
    versions = client.get_latest_versions(model_name, stages=["None"])
    if not versions:
        raise RuntimeError(f"No candidate model version found in stage 'None' for '{model_name}'.")
    return max(versions, key=lambda version: int(version.version))


def get_latest_production_version(client: MlflowClient, model_name: str):
    versions = client.get_latest_versions(model_name, stages=["Production"])
    if not versions:
        return None
    return max(versions, key=lambda version: int(version.version))


def get_run_accuracy(client: MlflowClient, run_id: str) -> float:
    run = client.get_run(run_id)
    accuracy = run.data.metrics.get("accuracy")
    if accuracy is None:
        raise RuntimeError(f"Run {run_id} has no logged 'accuracy' metric.")
    return accuracy


def passes_quality_gate(accuracy: float, threshold: float = QUALITY_GATE_MIN_ACCURACY) -> bool:
    return accuracy >= threshold


def select_backtest_dataset(
    dataset: pd.DataFrame,
    match_count: int = BACKTEST_MATCH_COUNT,
) -> pd.DataFrame:
    if match_count <= 0:
        raise RuntimeError("QUALITY_GATE_BACKTEST_MATCH_COUNT must be greater than 0.")

    backtest = dataset.copy()
    if "utc_date" in backtest.columns:
        backtest = backtest.sort_values("utc_date")
    elif "date" in backtest.columns:
        backtest = backtest.sort_values("date")

    return backtest.tail(match_count)


def evaluate_model_on_backtest(model, backtest_dataset: pd.DataFrame) -> float:
    if backtest_dataset.empty:
        raise RuntimeError("Backtest dataset is empty.")

    predictions = model.predict(backtest_dataset[FEATURE_COLUMNS])
    return accuracy_score(backtest_dataset[TARGET_COLUMN], predictions)


def load_model_version(model_name: str, version: str):
    return mlflow.sklearn.load_model(f"models:/{model_name}/{version}")


def beats_champion(
    candidate_accuracy: float,
    champion_accuracy: float | None,
    min_improvement: float = BACKTEST_MIN_IMPROVEMENT,
) -> bool:
    if champion_accuracy is None:
        return True
    return candidate_accuracy > champion_accuracy + min_improvement


def main() -> None:
    load_env_file()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        raise RuntimeError("MLFLOW_TRACKING_URI must be set to run the promotion pipeline.")
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()
    candidate = get_latest_candidate_version(client, REGISTERED_MODEL_NAME)
    training_accuracy = get_run_accuracy(client, candidate.run_id)
    production = get_latest_production_version(client, REGISTERED_MODEL_NAME)

    dataset = load_dataset(DATASET_PATH)
    backtest_dataset = select_backtest_dataset(dataset)
    candidate_model = load_model_version(REGISTERED_MODEL_NAME, candidate.version)
    candidate_backtest_accuracy = evaluate_model_on_backtest(candidate_model, backtest_dataset)

    champion_backtest_accuracy = None
    if production is not None:
        champion_model = load_model_version(REGISTERED_MODEL_NAME, production.version)
        champion_backtest_accuracy = evaluate_model_on_backtest(champion_model, backtest_dataset)

    client.transition_model_version_stage(
        name=REGISTERED_MODEL_NAME,
        version=candidate.version,
        stage="Staging",
        archive_existing_versions=False,
    )
    print(
        f"Candidate version {candidate.version} deployed to Staging "
        f"(training accuracy={training_accuracy:.3f}, "
        f"backtest accuracy={candidate_backtest_accuracy:.3f} on {len(backtest_dataset)} matches)."
    )

    if production is not None:
        print(
            f"Current champion version {production.version} backtest accuracy="
            f"{champion_backtest_accuracy:.3f}."
        )
    else:
        print("No Production champion found; candidate only needs to pass the minimum threshold.")

    threshold_passed = passes_quality_gate(candidate_backtest_accuracy)
    champion_beaten = beats_champion(candidate_backtest_accuracy, champion_backtest_accuracy)

    if threshold_passed and champion_beaten:
        client.transition_model_version_stage(
            name=REGISTERED_MODEL_NAME,
            version=candidate.version,
            stage="Production",
            archive_existing_versions=True,
        )
        print(
            f"Quality gate passed: candidate backtest accuracy "
            f"{candidate_backtest_accuracy:.3f} >= {QUALITY_GATE_MIN_ACCURACY} "
            f"and beats champion. "
            f"Promoted version {candidate.version} to Production."
        )
    else:
        reason = []
        if not threshold_passed:
            reason.append(
                f"backtest accuracy {candidate_backtest_accuracy:.3f} "
                f"< {QUALITY_GATE_MIN_ACCURACY}"
            )
        if not champion_beaten:
            reason.append(
                f"candidate {candidate_backtest_accuracy:.3f} does not beat champion "
                f"{champion_backtest_accuracy:.3f}"
            )
        print(
            f"Quality gate failed ({'; '.join(reason)}). "
            f"Version {candidate.version} stays in Staging; Production is unchanged."
        )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
