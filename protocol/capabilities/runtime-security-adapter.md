# Runtime Security Adapter

PGSA should not pretend to be a kernel security product. Instead, it defines a stable event format so tools such as Nono, Falco/eBPF, container telemetry, or dev-box audit logs can feed project-governance evidence.

Reference artifacts:

- `protocol/adapters/nono_runtime_adapter_spec.md`
- `protocol/adapters/falco_runtime_evidence_adapter_spec.md`
- `pgsa/evidence/runtime_evidence.jsonl`
