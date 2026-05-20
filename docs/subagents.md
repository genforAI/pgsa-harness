# Subagents

PGSA can model work at three levels:

```text
Project Group
  -> Session
      -> Subagents
```

## Definitions

- Project Group: the whole project-coherence boundary.
- Session: a project-level ownership boundary.
- Subagent: a worker inside a session.
- Session Master: the owner that synthesizes subagent outputs into
  project-level PGSA artifacts.

## Rule

Subagent conflicts stay inside a session if they do not affect external
contracts, review gates, integration readiness, or other sessions.

If a subagent conflict affects a public contract or another session, escalate it
to a project-level merge proposal.

## Example

```text
Backend Session
  API subagent
  schema subagent
  test subagent
```

If API/schema disagreement changes a public API contract, then update or create:

```text
pgsa/contracts/api.project.v1.json
pgsa/merge_proposals/mp_backend_api_schema_conflict.md
pgsa/reviews/backend_review.md
pgsa/integration/integration_report.json
```

Subagent outputs should not bypass the session owner. They should be summarized
into the session summary, contract updates, review requests, or merge proposals.

PGSA v0.1 models this ownership and escalation path. It does not include a
runtime subagent scheduler; scheduling remains the responsibility of the agent
platform, user workflow, or surrounding harness.
