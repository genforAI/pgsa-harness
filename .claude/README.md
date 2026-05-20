# Claude Code Workflow Notes

PGSA Harness can be used around Claude Code-style workflows by reading and
writing repo-local `pgsa/` artifacts.

This folder is a tool-specific workflow surface. It does not modify Claude Code
internals and does not claim Claude Code product benchmark evidence.

Recommended flow:

1. Read `AGENTS.md`.
2. Identify the active session in `pgsa/sessions.yaml`.
3. Read `pgsa/harness/<session>.md`.
4. Update contracts, summaries, merge proposals, reviews, integration reports,
   and ledger events as needed.
5. Run `pgsa validate` and `pgsa drift-report` before handoff.

