# Claude Hook Notes

These are hook notes for local Claude Code-style configurations.

They are not auto-enabled. If a user enables hooks, they should map to the same
PGSA lifecycle:

- session start: read or export session harness context;
- post tool use: check contract, summary, review, and merge-proposal impact;
- stop: run validation and drift reporting before handoff.

