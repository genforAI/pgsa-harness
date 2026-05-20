# PGSA Harness Docs

This folder is for engineering notes that explain the protocol architecture,
adapter model, evidence boundary, and claim boundaries.

Current v0.1 status:

- Agent-facing harness assets live under `AGENTS.md`, `.codex/`, `.agents/`,
  `skills/`, `commands/`, `hooks/`, `templates/`, and `rules/`.
- Protocol templates and validators live under `core/`.
- CLI implementation lives under `pgsa_cli/`.
- Adapter docs and Codex prompt scaffolds live under `adapters/`.
- Project-defined role examples and schemas live under `roles/`.
- Public evidence boundary notes live under `evidence/local-generated-git-worktree/`.

V0.1 is a local workflow/protocol package. It is not a product benchmark.

## Architecture Clarification Docs

- `custom-session-roles.md`: project-defined roles and session bindings.
- `role-binding-and-external-harness.md`: adapting roles from external harnesses.
- `pgsa-vs-pr-gittree.md`: PGSA compared with PR, GitTree, and worktree workflows.
- `conflict-lifecycle.md`: how PGSA records project conflicts.
- `cli-boundary.md`: what the CLI can and cannot decide.
- `subagents.md`: Project Group -> Session -> Subagents model.
- `why-project-coherence-layer.md`: why PGSA focuses on project-state continuity.
