import os
import sys
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient

from scripts.train_baseline_model import REGISTERED_MODEL_NAME, load_env_file

QUALITY_GATE_MIN_ACCURACY = float(os.getenv("QUALITY_GATE_MIN_ACCURACY", "0.5"))


def get_latest_candidate_version(client: MlflowClient, model_name: str):
    versions = client.get_latest_versions(model_name, stages=["None"])
    if not versions:
        raise RuntimeError(f"No candidate model version found in stage 'None' for '{model_name}'.")
    return max(versions, key=lambda version: int(version.version))


def get_run_accuracy(client: MlflowClient, run_id: str) -> float:
    run = client.get_run(run_id)
    accuracy = run.data.metrics.get("accuracy")
    if accuracy is None:
        raise RuntimeError(f"Run {run_id} has no logged 'accuracy' metric.")
    return accuracy


def passes_quality_gate(accuracy: float, threshold: float = QUALITY_GATE_MIN_ACCURACY) -> bool:
    return accuracy >= threshold


def main() -> None:
    load_env_file()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        raise RuntimeError("MLFLOW_TRACKING_URI must be set to run the promotion pipeline.")
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()
    candidate = get_latest_candidate_version(client, REGISTERED_MODEL_NAME)
    accuracy = get_run_accuracy(client, candidate.run_id)

    client.transition_model_version_stage(
        name=REGISTERED_MODEL_NAME,
        version=candidate.version,
        stage="Staging",
        archive_existing_versions=False,
    )
    print(f"Candidate version {candidate.version} (accuracy={accuracy:.3f}) deployed to Staging.")

    if passes_quality_gate(accuracy):
        client.transition_model_version_stage(
            name=REGISTERED_MODEL_NAME,
            version=candidate.version,
            stage="Production",
            archive_existing_versions=True,
        )
        print(
            f"Quality gate passed (accuracy {accuracy:.3f} >= {QUALITY_GATE_MIN_ACCURACY}). "
            f"Promoted version {candidate.version} to Production."
        )
    else:
        print(
            f"Quality gate failed (accuracy {accuracy:.3f} < {QUALITY_GATE_MIN_ACCURACY}). "
            f"Version {candidate.version} stays in Staging; Production is unchanged."
        )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
