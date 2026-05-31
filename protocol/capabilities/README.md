# PGSA Advanced Capability Packs

These packs extend the Goal 1 repo-local project-state protocol without changing the core principle: tools remain optional consumers and producers of inspectable PGSA artifacts.

Capability packs are grouped into four layers:

1. **Harness layer**: factory mode, long-running worker harness, contract-to-gate blueprints, scenario tests, review routing.
2. **Runtime security layer**: session runtime profiles, capability contracts, signed skills, runtime evidence adapters, rollback-compatible evidence.
3. **Audit layer**: agent flight recorder events and project coherence ledger linkage.
4. **Research extension layer**: cognitive audit notes for NLA/ALM-style hypotheses.

A project can use the core `pgsa/` workspace alone, or initialize optional advanced artifacts with `pgsa init --advanced`.
