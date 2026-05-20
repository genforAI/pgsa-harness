# TeamTask ProjectBoard PGSA Example

This is a minimal PGSA Harness example project.

It demonstrates the files created by:

```bash
python3 -m pgsa_cli.main --root examples/teamtask-projectboard init
python3 -m pgsa_cli.main --root examples/teamtask-projectboard validate
python3 -m pgsa_cli.main --root examples/teamtask-projectboard drift-report
python3 -m pgsa_cli.main --root examples/teamtask-projectboard harness --session backend
```

The important files are under `pgsa/`:

- `pgsa/harness/*.md`: per-session harness files.
- `pgsa/contracts/*.json`: shared project contracts.
- `pgsa/state/*.summary.md`: session summaries.
- `pgsa/reviews/`: review gates.
- `pgsa/integration/integration_report.json`: integration readiness.
- `pgsa/ledger/coherence_ledger.jsonl`: append-only project memory.
- `pgsa/reports/drift_report.json`: generated drift report.

