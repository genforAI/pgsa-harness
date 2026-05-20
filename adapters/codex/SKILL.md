---
name: pgsa-project-coherence
description: Use when a coding task spans multiple project areas, contracts, session state, review, integration, or merge/conflict risk. Helps Codex-style workflows maintain PGSA project-coherence artifacts while editing code.
---

# PGSA Project Coherence Harness

PGSA Harness gives Codex workflows a project layer without modifying Codex internals.

PGSA Harness lives in the repo. Codex reads PGSA context, writes PGSA artifacts after tasks, and uses validators to check whether project-coherence artifacts are present.

This is not a Codex internal modification. This is not a Codex product benchmark.

For simple one-file edits with no contract, review, integration, or session-state risk, do not force PGSA. Use the harness when project coherence matters.

## When To Use

Use PGSA when:

- the task changes APIs, schemas, components, permissions, docs, or tests;
- multiple sessions or modules are involved;
- there is integration risk;
- the user asks for maintainability, project coherence, or long-running work;
- the project contains a `pgsa/` folder and the task has project-coherence risk.

## Workflow

1. Inspect `pgsa/project.yaml`.
2. Identify the relevant session in `pgsa/sessions.yaml`.
3. Read `pgsa/harness/<session>.md`.
4. Read current contracts and session summaries.
5. Perform the coding task.
6. Update session summary.
7. Update affected contracts.
8. If cross-session conflict exists, create a merge proposal.
9. Write a coherence ledger event.
10. Run review/integration checks if relevant.
11. Output a concise project-coherence summary.

## Example: Backend API Change

1. Codex reads `pgsa/project.yaml` and `pgsa/sessions.yaml`.
2. Codex identifies the backend session scope.
3. Codex edits backend API files.
4. Codex updates the affected API contract.
5. Codex updates backend session summary.
6. Codex creates a merge proposal if frontend/docs/security are affected.
7. Codex appends a ledger event.
8. The user or wrapper runs `pgsa validate` and `pgsa drift-report`.

## Required Artifacts

Depending on task type, update:

- `pgsa/state/<session>.summary.md`;
- `pgsa/harness/<session>.md`;
- `pgsa/contracts/*.json`;
- `pgsa/merge_proposals/*.md`;
- `pgsa/reviews/*.md`;
- `pgsa/integration/integration_report.json`;
- `pgsa/ledger/coherence_ledger.jsonl`.

## When Not To Use

For simple one-file edits with no contract, review, integration, or session-state risk, do not force PGSA. Use the harness when project coherence matters.

## Rule

Do not only say the project is coherent. Write the artifact that makes the project state inspectable.
