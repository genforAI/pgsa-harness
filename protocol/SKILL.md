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
2. Read `pgsa/sessions.yaml`, including the active session's `role`,
   `produces`, `consumes`, `must_read`, `must_update`, and `handoff_to`.
3. Identify the active session.
4. Read `pgsa/harness/<session>.md`.
5. If launched from `pgsa/session_agents/<session>/` or a sibling session
   folder, read `PGSA_SESSION.json` and `AGENTS.md` there; treat them as launch
   pointers back to the same registered session, not as a second registry.
6. If no session agent folder exists and this is a long-running or restartable
   session, create or update `pgsa/session_agents/<session>/AGENTS.md`,
   `SKILL.md`, and `PGSA_SESSION.json` yourself. Use
   `protocol/session-agents/README.md` as the template and point the files back
   to `pgsa/sessions.yaml`, `pgsa/harness/<session>.md`,
   `pgsa/state/<session>.summary.md`, and
   `pgsa/skills/signed_skill_manifest.yaml`.
7. Read relevant contracts, summaries, merge proposals, reviews, integration
   reports, and ledger events.
8. Check whether this project defines custom roles under `protocol/roles/` or
   `pgsa/sessions.yaml`.
9. Perform the task.
10. Update the session summary.
11. Update affected contracts and their `review_state`.
12. Update review/integration artifacts when readiness changes.
13. Create or update a merge proposal if another session may now be
   inconsistent.
14. Append a coherence ledger event. If multiple sessions are running in
    parallel, write a pending event under `pgsa/ledger/pending/*.json` and let
    the reviewer/integration session append it to `coherence_ledger.jsonl`.
15. If optional advanced artifacts exist, read relevant `gates/`, `runtime/`,
    `skills/`, `evidence/`, `factory/`, `scenarios/`, and `audits/` files before
    making review or permission claims. For imported skills, use only accepted
    entries in `pgsa/skills/signed_skill_manifest.yaml` whose `applies_to`
    contains the active session or `*`.
16. Run validation and drift reporting before handoff when available.

## Required Artifacts

- `pgsa/harness/<session>.md`
- `pgsa/session_agents/<session>/AGENTS.md` (optional launch wrapper)
- `pgsa/session_agents/<session>/PGSA_SESSION.json` (optional launch pointers)
- `pgsa/contracts/*.json`
- `pgsa/state/*.summary.md`
- `pgsa/merge_proposals/*.md`
- `pgsa/reviews/*`
- `pgsa/integration/integration_report.json`
- `pgsa/ledger/coherence_ledger.jsonl`
- `pgsa/reports/drift_report.json`

Optional advanced artifacts:

- `pgsa/gates/verification_blueprint.yaml`
- `pgsa/gates/review_router.yaml`
- `pgsa/runtime/session_runtime_profile.yaml`
- `pgsa/runtime/capability_contract.yaml`
- `pgsa/skills/signed_skill_manifest.yaml`
- `pgsa/evidence/runtime_evidence.jsonl`
- `pgsa/factory/factory_plan.yaml`
- `pgsa/scenarios/*.yaml`
- `pgsa/audits/cognitive_audit_note.md`

## Coordination Rule

Sessions stay decoupled by default. They coordinate through contracts, merge
proposals, review gates, integration reports, and ledger events. Do not require
another agent's chat history to understand project state.

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
