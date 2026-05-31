# PGSA Artifact Schemas

PGSA Harness Core v1.1 uses JSON-compatible structured files, YAML files, JSONL
ledgers, and Markdown artifacts. Schemas document the expected artifact shape;
the optional CLI performs lightweight validation but is not the semantic source
of truth.

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

Validation logic currently lives in
`tools/python/pgsa_core/validators/artifacts.py`.


## Optional Advanced Schemas

Advanced schemas describe optional project-state artifacts for Goal 2 capability
fusion: verification blueprints, review routers, session runtime profiles,
capability contracts, signed skill manifests, runtime evidence events, factory
plans, scenario tests, and cognitive audit notes.

These schemas describe repo-local evidence and routing surfaces. They do not
turn PGSA into a runtime enforcement product, CI system, security monitor, or
model-interpretability guarantee.
