# PGSA Session Harness: docs_security_integration

## Session scope
- docs
- security checklist
- integration readiness

## Required protocol

1. Read `pgsa/project.yaml` and `pgsa/sessions.yaml`.
2. Stay inside this session scope unless a contract or integration issue requires coordination.
3. Before changing shared behavior, inspect relevant contracts in `pgsa/contracts/`.
4. After local work, update this session summary in `pgsa/state/docs_security_integration.summary.md`.
5. If API, schema, component, permission, or docs assumptions changed, update the affected contract or review artifact.
6. If another session may now be inconsistent, create or update a merge proposal in `pgsa/merge_proposals/`.
7. Append a ledger event in `pgsa/ledger/coherence_ledger.jsonl`.
8. Run `pgsa validate` and `pgsa drift-report` before handoff.

## Conflict rule

Do not resolve semantic project conflict with a vague note. Use a contract update,
review gate, integration blocker, or merge proposal so the next session can see
the exact project-state issue.
