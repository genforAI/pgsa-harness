---
name: pgsa-project-coherence
description: Use when a coding-agent task affects project coherence, contracts, review, integration, or multi-session state.
---

# PGSA Project Coherence

Use this skill when a task can change shared project assumptions across
sessions, modules, APIs, schemas, permissions, docs, review state, or final
integration.

PGSA Harness is repo-local. It does not live inside the model. It lives inside
the repository.

## Workflow

1. Read `pgsa/project.yaml`.
2. Read `pgsa/sessions.yaml`.
3. Identify the active session.
4. Read `pgsa/harness/<session>.md`.
5. Read relevant contracts, summaries, merge proposals, reviews, integration
   reports, and ledger events.
6. Check whether this project defines custom roles under `roles/` or
   `pgsa/sessions.yaml`.
7. Perform the task.
8. Update the session summary.
9. Update affected contracts or review/integration artifacts.
10. Create or update a merge proposal if another session may now be
   inconsistent.
11. Append a coherence ledger event.
12. Run validation and drift reporting before handoff when available.

## Required Artifacts

- `pgsa/harness/<session>.md`
- `pgsa/contracts/*.json`
- `pgsa/state/*.summary.md`
- `pgsa/merge_proposals/*.md`
- `pgsa/reviews/*`
- `pgsa/integration/integration_report.json`
- `pgsa/ledger/coherence_ledger.jsonl`
- `pgsa/reports/drift_report.json`

## Claim Boundary

Do not claim PGSA beats Codex, Claude Code, Grok Build, OpenAI, Anthropic, or
any hosted product. Current evidence is local generated git-worktree
architecture-protocol evidence only.

## Role, CLI, And Conflict Boundaries

- Roles are project-defined; example roles are not hardcoded by PGSA.
- The CLI is helper automation, not semantic authority.
- PGSA does not automatically solve every conflict. It makes project conflicts
  explicit, reviewable, and resumable.
- Subagents work inside sessions. Session owners synthesize their output into
  project-level artifacts.
