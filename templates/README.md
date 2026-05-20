# PGSA Templates

These templates describe the repo-local artifacts copied into a target
repository's `pgsa/` folder.

The Python initializer uses `core/templates/` as its implementation source. This
root `templates/` folder is the public-facing template surface for humans and
agents to inspect.

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

Role and subagent templates:

- `role.template.yaml`
- `session_binding.template.yaml`
- `subagent_task_card.template.md`
- `session_master_summary.template.md`
