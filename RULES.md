# PGSA Harness Rules

These rules apply to humans and coding agents working with this repository.

## Product framing

- PGSA Harness Core is a repo-local project-coherence layer for coding-agent workflows.
- It lives inside the repository, not inside Codex, Claude Code, Grok Build, or any model.
- Codex-style workflows can read and write PGSA artifacts as a workflow layer.

## Claim boundaries

Do not assert commercial-tool superiority, internal product modification, or measured product improvement unless a real Level 3 run proves it.

In public copy, avoid turning local generated protocol evidence into commercial product evidence.

## Workflow rules

- Define roles per project. Do not treat example frontend/backend/docs/security roles as fixed PGSA roles.
- Update contracts when shared API/schema/component/permission behavior changes.
- Update session summaries when a session changes code, docs, tests, contracts, reviews, or integration state.
- Create merge proposals when local changes may break another session's assumptions.
- Append ledger events for project-coherence relevant changes.
- Run validation / drift-report before handoff when possible.

## Conflict and CLI rules

- PGSA does not automatically solve every conflict. It makes project conflicts explicit, reviewable, and resumable.
- The CLI is helper automation, not semantic authority.
- Review and integration sessions produce authoritative semantic synthesis from PGSA artifacts.
- PGSA can sit before, during, or above PR/worktree workflows; it does not replace them.
