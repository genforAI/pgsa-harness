# PGSA Adapter Specifications

Adapters are optional bridges from external tools into repo-local PGSA artifacts. They must not become mandatory runtime dependencies.

An adapter should produce inspectable files under `pgsa/`, usually `pgsa/evidence/runtime_evidence.jsonl`, `pgsa/runtime/capability_requests/`, or review/integration artifacts.
