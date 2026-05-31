# Agent Instructions

This repository is PGSA Harness Core: an agent-first, repo-local
project-coherence protocol.

The protocol is the files under `protocol/` and the generated `pgsa/` artifact
layer in target projects. Python under `tools/python/` is optional user tooling,
not the agent-facing product surface.

## Working Rules

1. Start with `README.md`, then `protocol/SKILL.md`.
2. Treat `pgsa/` artifacts as project state, not generated clutter.
3. Treat `pgsa/harness/<session>.md` as the per-session operating surface.
4. Read session registration fields before work: `role`, `produces`,
   `consumes`, `must_read`, `must_update`, and `handoff_to`.
5. When shared behavior changes, update the affected contract, summary, review,
   integration report, merge proposal, or ledger event.
6. Do not present `export-context` as the communication mechanism. It is only a
   convenience packet assembled from repo-local artifacts.
7. Do not present the optional Python CLI as semantic authority.
8. Do not claim PGSA automatically solves conflicts. It makes project conflicts
   explicit, reviewable, and resumable.
9. Do not claim product benchmark evidence or that PGSA lives inside Codex,
   Claude Code, Grok Build, or any model.

## Entry Points

- `protocol/SKILL.md`: primary agent workflow.
- `protocol/artifact-map.md`: artifact meanings.
- `protocol/templates/`: starter PGSA artifacts.
- `protocol/schemas/`: structured artifact schemas.
- `protocol/rules/`: short boundaries.
- `examples/teamtask-projectboard/`: complete example `pgsa/` layer.
- `tools/python/`: optional CLI for users.

## Validation

From the repository root:

```bash
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard validate
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard drift-report
python3 -m unittest discover -s tools/python/tests -t tools/python
python3 tools/scripts/validate_release.py --root .
```
