# PGSA Artifact Schemas

V0.1 uses JSON-compatible structured files and Markdown artifacts rather than a
formal schema runtime.

Required artifact families:

- `pgsa/project.yaml`
- `pgsa/sessions.yaml`
- `pgsa/contracts/*.json`
- `pgsa/state/*.summary.md`
- `pgsa/merge_proposals/*.md`
- `pgsa/reviews/*.md`
- `pgsa/integration/integration_report.json`
- `pgsa/ledger/coherence_ledger.jsonl`
- `pgsa/reports/drift_report.json`

Validation logic currently lives in `core/validators/artifacts.py`.
