# PGSA Factory Mode

PGSA Factory Mode maps a product requirement into a session DAG, then lets sessions execute in bounded scopes while evidence flows back into contracts, gates, reviews, and the coherence ledger.

It does not claim fully autonomous software factories. PGSA is the governance layer for dark-factory-like workflows: intake, session decomposition, bounded execution, verification, integration, rework, and escalation.

Core artifacts:

- `pgsa/factory/factory_plan.yaml`
- `pgsa/gates/verification_blueprint.yaml`
- `pgsa/integration/integration_report.json`
- `pgsa/ledger/coherence_ledger.jsonl`

Factory tasks should name the owning session, expected outputs, required evidence, and dependency edges.
