# Advanced Capability Boundary

Advanced PGSA artifacts must remain repo-local project-state files. They may describe runtime enforcement, dev-box evidence, review routing, or cognitive audit hypotheses, but they must not make PGSA a mandatory daemon, database, hosted service, kernel security product, CI replacement, or model-interpretability guarantee.

Evidence strength order:

1. Runtime/test/CI evidence
2. Contract diffs and review decisions
3. Coherence ledger events
4. Cognitive audit hypotheses

Adapters should write or reference evidence; they should not become the primary project surface.
