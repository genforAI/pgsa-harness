# PGSA Session Harness: backend

## Session Scope
- backend API
- schema
- permission logic

## Coordination Contract

This session is autonomous inside its scope. It coordinates with other sessions
only through repo-local PGSA artifacts.

## Required Protocol

1. Read `pgsa/project.yaml`.
2. Read `pgsa/sessions.yaml` and confirm this session's `role`, `produces`,
   `consumes`, `must_read`, `must_update`, and `handoff_to` fields.
3. Read relevant contracts in `pgsa/contracts/`.
4. Read open merge proposals in `pgsa/merge_proposals/`.
5. Read relevant session summaries in `pgsa/state/`.
6. Do the local task inside this session scope.
7. Update this session summary in `pgsa/state/backend.summary.md`.
8. If shared behavior changed, update the affected contract and its
   `review_state`.
9. If a consumer may now be stale, create or update a merge proposal.
10. If integration should be blocked, update `pgsa/integration/integration_report.json`.
11. Append a ledger event in `pgsa/ledger/coherence_ledger.jsonl`.
12. Run validation and drift reporting before handoff when available.

## Conflict Rule

Do not resolve semantic project conflict with a vague note. Use one of:

- contract update;
- review gate decision;
- integration blocker;
- merge proposal;
- ledger decision event.

The next session must be able to see the exact project-state issue without chat
history.
