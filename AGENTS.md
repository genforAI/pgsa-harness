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
   `owner_scope`, `consumes`, `must_read`, `must_update`, `handoff_to`, and
   `escalation_policy`.
5. When shared behavior changes, update the affected contract, summary, review,
   integration report, merge proposal, or ledger event.
6. Do not present `export-context` as the communication mechanism. It is only a
   convenience packet assembled from repo-local artifacts.
7. Do not present the optional Python CLI as semantic authority.
8. Do not describe PGSA as PR automation. PRs review code diffs; PGSA records
   session identity, semantic project-state drift, and handoff obligations before
   and around PR review.
9. Do not claim PGSA automatically solves conflicts. It makes project conflicts
   explicit, reviewable, and resumable.
10. When writing public positioning, emphasize session registration,
   `must_read`/`must_update`, semantic continuity, contracts, integration state,
   ledger records, and optional v1.1 advanced packs.
11. Do not claim product benchmark evidence or that PGSA lives inside Codex,
   Claude Code, Grok Build, or any model.
12. For long-running PGSA sessions, prefer agent-owned session wrappers: after
   reading `pgsa/sessions.yaml`, the active session may create or refresh
   `pgsa/session_agents/<session>/AGENTS.md`, `SKILL.md`, and
   `PGSA_SESSION.json`. These files must point back to the shared PGSA root and
   must not become a second registry.
13. Per-session `SKILL.md` files route into the project-level
   `pgsa/skills/signed_skill_manifest.yaml`. Do not copy raw imported skill
   instructions into a session folder or activate anything from
   `pgsa/imports/sources/` unless the source is explicitly in that session's
   `must_read` or the session is `external_import_review`.

## Entry Points

- `protocol/SKILL.md`: primary agent workflow.
- `protocol/artifact-map.md`: artifact meanings.
- `protocol/templates/`: starter PGSA artifacts.
- `protocol/schemas/`: structured artifact schemas.
- `protocol/rules/`: short boundaries.
- `protocol/session-agents/README.md`: self-bootstrap pattern for per-session
  launch folders.
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
