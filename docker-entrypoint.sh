#!/bin/sh
set -e

if [ -n "$DAGSHUB_USERNAME" ] && [ -n "$DAGSHUB_TOKEN" ]; then
  if [ ! -d .git ]; then
    git init -q
  fi
  mkdir -p .dvc
  cat > .dvc/config.local <<CONFIG
['remote "dagshub"']
    auth = basic
    user = $DAGSHUB_USERNAME
    password = $DAGSHUB_TOKEN
CONFIG
  echo "Pulling data from DVC remote..."
  dvc pull -f
else
  echo "DAGSHUB_USERNAME/DAGSHUB_TOKEN not set, skipping dvc pull."
fi

exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
