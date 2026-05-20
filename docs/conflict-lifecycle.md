# Conflict Lifecycle

PGSA does not automatically solve every conflict.

It makes project conflicts explicit, reviewable, and resumable.

## File Conflict vs Project Conflict

```text
File conflict = two edits collide in Git.
Project conflict = multiple local decisions no longer compose.
```

Project conflicts include:

- contract drift;
- stale assumptions;
- docs describing old behavior;
- review state mismatch;
- integration readiness failure;
- security or permission mismatch;
- test expectation mismatch.

## Lifecycle

```text
session scope
-> local change
-> contract impact check
-> affected sessions
-> state summary update
-> semantic merge proposal
-> review gate
-> integration report
-> ledger event
-> agent-generated synthesis
```

The synthesis may be created by a review session, integration session, session
owner, or human maintainer. The CLI can surface missing artifacts, but it is not
the semantic authority.

## Example

```text
Backend session changes API response shape.
Frontend session still expects old fields.
Docs session describes the old schema.
Security session adds a permission rule.
No Git conflict appears.
But the project is semantically inconsistent.
```

PGSA records it through artifacts:

```text
pgsa/contracts/api.project.v1.json
pgsa/state/backend.summary.md
pgsa/merge_proposals/mp_api_shape_change.md
pgsa/reviews/frontend_review.md
pgsa/integration/integration_report.json
pgsa/ledger/coherence_ledger.jsonl
```

The artifact trail makes the conflict inspectable and resumable. It does not
pretend the conflict is solved until the affected sessions or reviewers update
the project state.

