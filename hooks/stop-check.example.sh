#!/usr/bin/env sh
set -eu

ROOT="${PGSA_ROOT:-.}"

python3 -m pgsa_cli.main --root "$ROOT" validate
python3 -m pgsa_cli.main --root "$ROOT" drift-report

