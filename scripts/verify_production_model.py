import os
import sys

import mlflow
from mlflow.tracking import MlflowClient

from scripts.train_baseline_model import REGISTERED_MODEL_NAME, load_env_file


def main() -> None:
    load_env_file()
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        raise RuntimeError("MLFLOW_TRACKING_URI must be set to verify the production model.")
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()
    versions = client.get_latest_versions(REGISTERED_MODEL_NAME, stages=["Production"])
    if not versions:
        raise RuntimeError(
            "No model version in the 'Production' stage. The model promotion gate "
            "(dev -> staging) must pass before deploying to production."
        )

    version = versions[0]
    print(f"Production model version {version.version} confirmed. Proceeding with deploy.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
