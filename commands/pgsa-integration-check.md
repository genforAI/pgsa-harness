# PGSA Integration Check Command

Use this command before treating multi-session work as coherent.

1. Read all current session summaries.
2. Read contracts and open merge proposals.
3. Read review-gate status.
4. Update `pgsa/integration/integration_report.json`.
5. Record unresolved blockers in `blocking_issues`.
6. Run `pgsa validate` and `pgsa drift-report`.
7. Append a ledger event if integration readiness changes.

