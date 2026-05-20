# PGSA vs PR, GitTree, And Worktree

PGSA is not a PR replacement and not a worktree replacement.

```text
PR is a code-change container.
Git/worktree is an execution isolation mechanism.
PGSA is a project-coherence transaction layer.
```

## What Each Layer Does

- Git handles file history.
- Worktree or GitTree-style workflows handle isolated workspaces.
- PRs handle code diffs, comments, CI, and merge approval.
- PGSA handles project-state transactions: contracts, session state, semantic
  merge proposals, review state, integration readiness, ledger events, and
  recovery state.

```text
PR asks: can this diff merge?
PGSA asks: does the project still make sense after multiple sessions changed it?
```

PGSA can operate before, during, or above PR workflows.

## Example 1: PR Can Pass While Project Still Drifts

```text
Backend changes an API.
Frontend still uses the old field names.
Docs describe the previous behavior.
Local tests pass.
A PR can still look reviewable.
But the project state is no longer coherent.
```

PGSA records the contract impact, affected sessions, review state, and
integration readiness so the drift is visible before final handoff.

## Example 2: Git Merge Can Succeed While Semantic Merge Fails

```text
No file-level conflict exists.
But API contract, UI assumption, docs, and security review no longer agree.
That is a project conflict, not a file conflict.
```

Git can merge the files. PGSA records the project conflict so a human or agent
can review and repair it.

## What PGSA Adds Above PRs

PGSA adds durable project-state artifacts:

- `pgsa/contracts/`
- `pgsa/state/`
- `pgsa/merge_proposals/`
- `pgsa/reviews/`
- `pgsa/integration/`
- `pgsa/ledger/`
- `pgsa/reports/`

Those artifacts help future sessions understand what changed, what remains
blocked, and why a local change may not compose with the rest of the project.

