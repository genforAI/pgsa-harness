# Codex Workflow Notes

PGSA Harness can be used around Codex-style workflows without modifying Codex
internals.

The working pattern is:

1. Read `README.md`.
2. Identify the relevant session in `pgsa/sessions.yaml`.
3. Read `pgsa/harness/<session>.md`.
4. Read relevant contracts and session summaries.
5. Perform the coding task.
6. Update the affected `pgsa/` artifacts.
7. Create a merge proposal when another session may now be inconsistent.
8. Append a coherence ledger event.
9. Run `pgsa validate` and `pgsa drift-report` before handoff.

`pgsa export-context --session <name>` can assemble those artifacts into one
Markdown packet for Codex to read. The packet is a convenience layer. The source
of truth remains the repo-local `pgsa/` files.

This is not a Codex product benchmark and not a Codex internal modification.

