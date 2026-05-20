# PGSA Artifact Map

- `project.yaml`: project identity, goals, modules, and acceptance criteria.
- `sessions.yaml`: durable session ownership and required updates.
- `harness/<session>.md`: per-session operating instructions.
- `contracts/*.json`: shared producer/consumer assumptions.
- `state/*.summary.md`: compressed session memory.
- `merge_proposals/*.md`: semantic conflict records.
- `reviews/*`: review-gate status.
- `integration/integration_report.json`: final integration readiness.
- `ledger/coherence_ledger.jsonl`: append-only project-coherence memory.
- `reports/drift_report.json`: generated drift and maintainability report.

