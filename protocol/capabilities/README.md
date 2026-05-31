# PGSA Advanced Capability Packs

These packs extend the Goal 1 repo-local project-state protocol without changing the core principle: tools remain optional consumers and producers of inspectable PGSA artifacts.

Capability packs are optional and should be understood as artifact shapes, not
services that PGSA runs or enforces. They are grouped into four layers:

- **Core protocol**: contracts, session summaries, ledgers, merge proposals,
  reviews, and integration readiness.
- **Harness packs**: verification blueprints, scenario tests, review routing,
  and factory-style planning.
- **Runtime adapter specs**: session runtime profiles, capability contracts,
  signed skill provenance, runtime evidence, and external security/runtime
  adapter records.
- **Research notes**: cognitive audit notes for NLA/ALM-style hypotheses.

A project can use the core `pgsa/` workspace alone, or initialize optional advanced artifacts with `pgsa init --advanced`.

These packs do not turn PGSA into CI, a sandbox, a kernel monitor, an autonomous
factory, or a model-interpretability guarantee.
