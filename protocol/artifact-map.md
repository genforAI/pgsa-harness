# PGSA Artifact Map

- `project.yaml`: project identity, goals, modules, and acceptance criteria.
- `sessions.yaml`: durable session ownership, produced/consumed artifacts, required reads/updates, and handoff targets.
- `harness/<session>.md`: per-session operating instructions.
- `contracts/*.json`: shared producer/consumer assumptions, review state, acceptance tests, and breaking-change state.
- `state/*.summary.md`: compressed session memory.
- `merge_proposals/*.md`: semantic conflict records with decision owner, affected contracts, and resolution state.
- `reviews/*`: review-gate status and blocking issues.
- `integration/integration_report.json`: final integration readiness, blockers, open merge proposals, and contract review state.
- `ledger/coherence_ledger.jsonl`: append-only project-coherence memory.
- `ledger/pending/*.json`: optional per-session ledger event drafts for parallel
  agent work; reviewer appends accepted events into `coherence_ledger.jsonl`.
- `reports/drift_report.json`: generated drift and maintainability report.


## Optional Advanced Capability Artifacts

- `gates/verification_blueprint.yaml`: contract-to-gate checks, required evidence, and blocking policy.
- `gates/review_router.yaml`: risk-tiered review routing rules.
- `runtime/session_runtime_profile.yaml`: session-level read/write/command/network posture.
- `runtime/capability_contract.yaml`: default capabilities, approval-required actions, and denied resources.
- `runtime/capability_requests/`: optional request records for temporary elevation.
- `skills/signed_skill_manifest.yaml`: signed skill/prompt/rule provenance manifest.
- `evidence/runtime_evidence.jsonl`: summarized agent run, runtime, command, permission, or adapter evidence.
- `factory/factory_plan.yaml`: session DAG for dark-factory-like execution planning.
- `scenarios/*.yaml`: acceptance/user-journey scenario tests.
- `audits/cognitive_audit_note.md`: NLA/ALM-style cognitive hypothesis note, never hard evidence.
