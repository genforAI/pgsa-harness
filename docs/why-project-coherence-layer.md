# Why A Project-Coherence Layer

As coding agents become better at local task completion, the bottleneck moves
upward.

The hard problem becomes project coherence:

- contracts;
- session state;
- semantic merge;
- review readiness;
- integration readiness;
- recoverable project memory.

PGSA does not invent structured files. It combines repo-local artifacts into a
project-coherence layer for long-running coding-agent workflows.

Existing harnesses often focus on execution, skills, memory, hooks, or
multi-tool setup. PGSA focuses on project-state continuity across sessions.

```text
PGSA is a bet that long-running coding-agent projects need a repo-local project
state layer, not just more agent execution.
```

This is why PGSA can sit above PR/worktree workflows. It records whether the
project still composes after many local sessions have changed different parts of
the system.

