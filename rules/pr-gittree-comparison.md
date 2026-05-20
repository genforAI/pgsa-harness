# PGSA vs PR / GitTree / Worktree

```text
PR is a code-change container.
Git/worktree is an execution isolation mechanism.
PGSA is a project-coherence transaction layer.
```

PR asks: can this diff merge?

PGSA asks: does the project still make sense after multiple sessions changed it?

PGSA can operate before, during, or above PR workflows. It records contracts,
session state, semantic merge proposals, review state, integration readiness,
ledger events, and recovery state.

PGSA is not a PR replacement.

