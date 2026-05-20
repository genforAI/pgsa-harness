# Security Policy

PGSA Harness Core stores project-coherence artifacts in the repository. Treat those artifacts as project state.

## Do not store secrets

Do not put secrets, API keys, private tokens, customer data, credentials, private model outputs, or proprietary internal logs into PGSA artifacts.

Potentially sensitive files include:

- `pgsa/contracts/`
- `pgsa/state/`
- `pgsa/merge_proposals/`
- `pgsa/reviews/`
- `pgsa/integration/`
- `pgsa/ledger/`
- `pgsa/reports/`

## External agent runs

A run without captured command, transcript, diffs, tests, versions, timing, and evaluator metadata must be labeled as a protocol run or dry run, not a real product run.

## Reporting issues

Open a GitHub issue with a minimal reproduction and avoid sharing secrets or private project data.
