# X Thread Candidates V1.18

## Thread 1: Builder Story

1.

Coding agents are getting better at finishing local tasks.

But the project can still drift.

2.

A backend session changes an API.

A frontend session keeps the old assumption.

Docs still describe the previous behavior.

Then integration happens, and the project no longer fits together.

3.

That is the failure mode I built PGSA Harness around.

Not an agent replacement. Not an internal product modification.

A repo-local project-coherence layer around coding-agent workflows.

4.

The harness asks sessions to leave behind inspectable artifacts:

- contracts
- session summaries
- merge proposals
- review state
- integration reports
- coherence ledger

5.

The gain I care about is not raw speed.

It is recoverability.

Can the next session understand what changed?

Can a semantic conflict become visible before final integration?

6.

Local generated git-worktree evidence:

semantic-drift suite:

```text
baseline final pass: 0 / 9
PGSA gate block: 9 / 9
PGSA final pass: 9 / 9
```

7.

No-drift controls:

```text
baseline final pass: 3 / 3
PGSA final pass: 3 / 3
PGSA over-block: 0 / 3
```

8.

This is local architecture-protocol evidence only.

Not a Codex / Claude / Grok product benchmark.

The next step is Level 3 testing with real tool transcripts, diffs, tests, and timing.

## Thread 2: Worktrees Angle

1.

Worktrees isolate execution.

They do not guarantee project coherence.

2.

You can merge files and still have a semantic contract mismatch:

backend returns one shape,
frontend expects another,
docs describe a third.

3.

PGSA Harness adds a project layer around the workflow:

contracts, summaries, semantic merge proposals, review gates, integration reports, and a ledger.

4.

In local generated git-worktree suites, PGSA gates surfaced semantic contract drift as explicit blockers.

The useful part was not speed.

It was making drift inspectable.

5.

Boundary: this is not a product benchmark.

No commercial-product comparison is being claimed.

It is a v0.1 repo-local harness and local protocol evidence.

## Reply Templates

### Is this Codex vs Claude?

No. This is not a Codex / Claude product benchmark. It is a repo-local project-coherence harness tested with local generated git-worktree suites.

### Does this modify Codex internally?

No. The current package has a Codex workflow adapter scaffold. It does not modify Codex internals.

### Does this prove convergence?

No. It supports a narrow local mechanism claim about surfacing semantic contract drift. Real convergence claims require stronger evidence.

### Why not just use worktrees?

Worktrees isolate execution. PGSA Harness focuses on project state: contracts, summaries, semantic merge proposals, review state, integration reports, and recovery.

### What is the next real test?

Level 3: fixed tasks run through real tools with prompts, transcripts, diffs, test logs, versions, timing, and the same evaluator.
