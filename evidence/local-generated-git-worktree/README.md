# Local Generated Git-Worktree Evidence

This folder summarizes the current public evidence boundary for PGSA Harness Core v0.1.

The current evidence is **local generated git-worktree architecture-protocol evidence**. It is not a Codex, Claude Code, Grok, OpenAI, Anthropic, or hosted product benchmark.

This release tree intentionally includes a summary placeholder rather than raw
metrics CSVs, figures, or historical review packets. Those materials should be
provided as a separate evidence archive or release artifact if they are needed
for audit continuity. Do not treat this folder as a raw benchmark dataset.

## Supported narrow claim

In local generated git-worktree suites, PGSA-gated artifacts surfaced semantic contract drift as review / merge blockers while not over-blocking the included no-drift controls.

## Raw counts

Positive semantic-drift suite:

```text
baseline final pass: 0 / 9
PGSA gate block: 9 / 9
PGSA final pass: 9 / 9
```

Negative no-drift controls:

```text
baseline final pass: 3 / 3
PGSA final pass: 3 / 3
PGSA over-block: 0 / 3
```

## Boundary

These counts support a local protocol claim about drift surfacing and no-drift control behavior. They do **not** prove:

- PGSA beats Codex;
- PGSA beats Claude Code;
- PGSA improves Codex by X%;
- PGSA is inside Codex;
- PGSA proves convergence;
- PGSA is production validated.

## Level 3 requirement

Real Codex / Claude / Grok claims require real tool commands, captured prompts and context, transcripts or stdout/stderr, before/after diffs, test logs, versions, timing metadata, and the same evaluator across conditions.
