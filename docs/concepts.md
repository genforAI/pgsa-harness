# Concepts

## Project Coherence

Local task completion is not the same as project coherence. A change can pass
in one module while leaving stale assumptions, contract drift, review debt, or
integration failure elsewhere.

## PGSA Artifacts

- `project.yaml`: project goal and module boundaries.
- `sessions.yaml`: durable session identities and ownership scopes.
- `harness/`: per-session operating instructions.
- `contracts/`: project contracts such as API shape and consumer expectations.
- `state/`: compressed session summaries.
- `merge_proposals/`: semantic merge or conflict records.
- `reviews/`: review-gate artifacts.
- `integration/`: final readiness and integration status.
- `ledger/`: append-only coherence events.
- `reports/`: drift and maintainability reports.

## Long-Running Session

A long-running session does not require a process that runs forever. PGSA treats
session continuity as durable identity plus recoverable artifacts.

## Session Communication

Sessions communicate through repo-local artifacts, not direct agent-to-agent
chat. Contracts, summaries, merge proposals, reviews, integration reports, and
ledger events are the shared project memory.
