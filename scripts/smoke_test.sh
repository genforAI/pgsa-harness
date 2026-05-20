#!/usr/bin/env sh
set -eu

ROOT="${1:-/tmp/pgsa-harness-smoke}"

rm -rf "$ROOT"
python3 -m pgsa_cli.main --root "$ROOT" init --force
python3 -m pgsa_cli.main --root "$ROOT" validate
python3 -m pgsa_cli.main --root "$ROOT" drift-report
python3 -m pgsa_cli.main --root "$ROOT" harness --session backend
python3 -m pgsa_cli.main --root "$ROOT" export-context --session backend --output "$ROOT/backend_context.md"

