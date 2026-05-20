# Session Lifecycle

Long-running session does not mean an agent process runs forever.

It means durable session identity, persistent artifacts, resumable context, and
unresolved drift tracking.

## Minimal Lifecycle

1. Session start.
   - Read `pgsa/project.yaml`.
   - Read `pgsa/sessions.yaml`.
   - Read `pgsa/harness/<session>.md`.

2. Local work.
   - Stay inside the session scope unless a shared contract or integration issue
     requires coordination.
   - Inspect relevant contracts before changing shared behavior.

3. Artifact update.
   - Update the session summary.
   - Update affected contracts, reviews, integration report, or merge proposal.
   - Append a ledger event.

4. Validation.
   - Run `pgsa validate`.
   - Run `pgsa drift-report`.

5. Handoff.
   - If drift remains, generate `pgsa continuation-prompt --session <name>` or
     create/update a merge proposal.
   - The next session resumes from repo-local artifacts, not previous chat
     history.

## Context Export

`pgsa export-context --session <name>` is optional. It packages the session
harness, related contracts, session summary, recent ledger events, and drift
report into one Markdown document for an agent to read.

The source of truth remains the `pgsa/` artifact layer.
