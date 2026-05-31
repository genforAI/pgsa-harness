#!/usr/bin/env sh
set -eu

ROOT="${1:-/tmp/pgsa-harness-smoke}"
REPO_ROOT="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
EMBEDDED="${ROOT}/pgsa-harness"

rm -rf "$ROOT"
mkdir -p "$EMBEDDED"
(
  cd "$REPO_ROOT"
  tar \
    --exclude='./.git' \
    --exclude='*/__pycache__' \
    --exclude='*/.pytest_cache' \
    --exclude='*.pyc' \
    --exclude='*.egg-info' \
    -cf - .
) | (
  cd "$EMBEDDED"
  tar -xf -
)

PYTHONPATH="${EMBEDDED}/tools/python"
export PYTHONPATH

python3 -m pgsa_cli.main --root "$ROOT" init --force
python3 -m pgsa_cli.main --root "$ROOT" validate
python3 -m pgsa_cli.main --root "$ROOT" drift-report
python3 -m pgsa_cli.main --root "$ROOT" harness --session backend
python3 -m pgsa_cli.main --root "$ROOT" export-context --session backend --output "$ROOT/backend_context.md"
