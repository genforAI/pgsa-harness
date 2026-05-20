# PGSA Lifecycle Hooks

This folder contains example lifecycle hooks for agent workflows.

They are examples only. They are not enabled automatically.

Possible hook points:

- `SessionStart`: export or print PGSA context for the active session.
- `PostToolUse`: remind the agent to update contracts, summaries, reviews, and
  ledger events after relevant file changes.
- `Stop`: run validation and drift reporting before handoff.

`pgsa watch` is a one-shot status check in v0.1, not a background process.
`pgsa queue list` reads an optional task queue if a project chooses to create
one. Session communication still happens through repo-local PGSA artifacts.
