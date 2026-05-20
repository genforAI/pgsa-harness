# PGSA Harness Core Architecture

PGSA Harness is a repo-local project-coherence protocol for coding-agent
workflows. It does not modify tool internals.

## Layers

1. Agent-facing harness layer: `AGENTS.md`, `.codex/`, `.agents/`, `skills/`,
   `commands/`, `hooks/`, `templates/`, and `rules/`.
2. Artifact layer: `pgsa/` session harness files, contracts, session summaries,
   merge proposals, reviews, integration reports, ledger, and drift reports.
3. Validation layer: checks artifact completeness, contract shape, unresolved
   merge proposals, and integration blockers.
4. Context layer: reads the repo-local artifacts and exports a session context
   packet when an agent benefits from a single Markdown input.
5. Adapter layer: skill/prompt documentation showing how Codex-style, Claude
   Code-style, Grok Build-style, or generic CLI workflows can follow the same
   repo-local protocol.

## Conflict Mechanism

PGSA does not coordinate sessions through live inter-agent messaging. The repo is
the communication medium.

When a session changes a shared assumption, it updates a contract or creates a
merge proposal. Dependent sessions read those artifacts and update their own
summary, review, integration, or contract files. The ledger records important
project-state events.

PGSA does not automatically solve every conflict. It makes project conflicts
explicit, reviewable, and resumable.

## Future-Facing Layer

As coding agents become better at local task completion, the bottleneck moves
upward. The hard problem becomes project coherence: contracts, session state,
semantic merge, review readiness, integration readiness, and recoverable project
memory.

PGSA does not invent structured files. It combines repo-local artifacts into a
project-coherence layer for long-running coding-agent workflows.

Existing harnesses often focus on execution, skills, memory, hooks, or
multi-tool setup. PGSA focuses on project-state continuity across sessions.

```text
PGSA is a bet that long-running coding-agent projects need a repo-local project
state layer, not just more agent execution.
```

## Boundary

Protocol runs can validate artifact flow. Product-level claims require real tool
transcripts and are out of scope for this v0.1 package.
