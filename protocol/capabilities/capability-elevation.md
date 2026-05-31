# Capability Elevation Broker

Capability elevation records and routes requests for authority beyond a
session's normal scope. It supports least-privilege workflows while still
allowing bounded temporary grants when a project reviewer accepts the risk.

A session should first be checked against
`pgsa/runtime/capability_contract.yaml`. If a requested read, write, command,
tool, or network capability exceeds the contract, the request becomes an
auditable decision artifact rather than an informal chat approval. PGSA records
the boundary and decision trail; it does not enforce permissions unless paired
with an external runtime or sandbox.

Reference artifacts:

- `pgsa/runtime/capability_contract.yaml`
- `pgsa/runtime/capability_requests/`
- `pgsa/evidence/runtime_evidence.jsonl`
