# Falco/eBPF Runtime Evidence Adapter Spec

Purpose: map kernel/runtime telemetry into PGSA project evidence.

Recommended normalized fields:

- `event_id`, `timestamp`, `session`, `agent`, `event_type`, `resource`, `action`, `risk`, `allowed_by`, `contract_scope`, `evidence_ref`

PGSA should only store summaries and references needed for project review. Raw telemetry can remain in the source security system.
