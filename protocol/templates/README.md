# PGSA Templates

These templates describe the repo-local artifacts copied into a target
repository's `pgsa/` folder.

This folder is the public-facing template surface for agents and humans. The
optional Python initializer mirrors this structure, but the protocol does not
depend on Python.

Primary generated files:

- `pgsa/project.yaml`
- `pgsa/sessions.yaml`
- `pgsa/harness/<session>.md`
- `pgsa/contracts/*.json`
- `pgsa/state/*.summary.md`
- `pgsa/merge_proposals/*.md`
- `pgsa/reviews/*.md`
- `pgsa/integration/integration_report.json`
- `pgsa/ledger/coherence_ledger.jsonl`
- `pgsa/ledger/pending/*.json` for parallel-session ledger event drafts
- `pgsa/imports/index.json` for external harness/skill/protocol import records
- `pgsa/imports/inbox/` for external sources waiting to be processed

Key coordination templates:

- `sessions.yaml`: session registration, produced/consumed artifacts, and handoff edges.
- `contract.template.json`: producer/consumer contract state and review state.
- `merge_proposal.template.md`: semantic conflict record.
- `integration_report.template.json`: final readiness and blocker state.
- `import_index.template.json`: indexed external sources that require review before promotion.

Role and subagent templates:

- `role.template.yaml`
- `session_binding.template.yaml`
- `subagent_task_card.template.md`
- `session_master_summary.template.md`


## Optional Advanced Templates

Advanced templates are copied only when a project intentionally uses advanced
mode or manually chooses the relevant files. They cover verification
blueprints, review routing, runtime profiles, capability contracts, signed
skills, factory-style plans, scenario tests, runtime evidence events,
capability requests, and cognitive audit notes.

The shipped advanced templates are JSON-compatible YAML: valid YAML syntax with
JSON-style formatting. This keeps them easy for agents and scripts to parse. A
project may reformat them as idiomatic YAML without changing the artifact shape.
