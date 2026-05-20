---
description: Maintain PGSA project-coherence artifacts for long-running multi-session coding work. Use when changes affect contracts, shared state, review, integration, or merge/conflict risk.
---

# PGSA Harness for Claude Code

This is a v0.1 scaffold. It documents optional skills/hooks integration surfaces but does not claim a completed Claude Code product benchmark.

Hooks require user configuration. They are not enabled automatically. PGSA Harness does not modify Claude Code internals.

Before editing:

- inspect `pgsa/project.yaml`
- identify session scope
- read `pgsa/harness/<session>.md`
- read relevant contracts and state summaries

After editing:

- update session summary
- update affected contracts
- create merge proposal if conflict exists
- record ledger event
- run review/integration checks when relevant

Lifecycle mapping:

```text
SessionStart -> export PGSA context
PostToolUse -> check changed files / contract impact
Stop -> require session summary / ledger / unresolved drift check
```
