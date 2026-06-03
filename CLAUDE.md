@AGENTS.md

# Claude Code Instructions

This repository is PGSA Harness Core: a repo-local project-coherence protocol
for coding-agent workflows.

Use the same project rules as `AGENTS.md`. In Claude Code, treat this file as
the durable entrypoint for repository behavior and `protocol/SKILL.md` as the
agent-facing PGSA workflow.

## PGSA Working Rules

1. Start with `README.md`, then `protocol/SKILL.md`.
2. Treat `protocol/` as the protocol source.
3. Treat target-project `pgsa/` artifacts as durable project state, not generated
   clutter.
4. Read session registration fields before work: `role`, `owner_scope`,
   `produces`, `consumes`, `must_read`, `must_update`, `handoff_to`, and
   `escalation_policy`.
5. Do not frame PGSA as PR automation or automatic conflict resolution.
6. Explain PGSA's value as session registration, semantic project-state
   continuity, and reviewable drift records around coding-agent work.
7. Do not claim PGSA replaces CI, sandboxing, PR review, code review, Codex,
   Claude Code, or any hosted product.

## Claude Code Usage Pattern

When asked to use PGSA in a target project, ask for or infer the active PGSA
session name, read `pgsa/sessions.yaml`, follow that session's `must_read` and
`must_update` fields, and create or update `pgsa/merge_proposals/*.md` only when
shared project assumptions drift.
