#!/usr/bin/env sh
set -eu

cat <<'MSG'
PGSA PostToolUse reminder:
- update session summary if project state changed
- update contracts if shared behavior changed
- create merge proposal if another session may be stale
- append a coherence ledger event before handoff
MSG

