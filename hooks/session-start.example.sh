#!/usr/bin/env sh
set -eu

SESSION="${PGSA_SESSION:-backend}"
ROOT="${PGSA_ROOT:-.}"

python3 -m pgsa_cli.main --root "$ROOT" harness --session "$SESSION"

