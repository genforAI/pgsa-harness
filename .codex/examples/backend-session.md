# Codex Example: Backend Session

1. Run:

```bash
python3 -m pgsa_cli.main --root . harness --session backend
```

2. Read `pgsa/contracts/api.project.v1.json`.
3. Make the backend change.
4. If response shape changes, update the contract.
5. If frontend or docs may be stale, create a merge proposal.
6. Update `pgsa/state/backend.summary.md`.
7. Append a ledger event.
8. Run:

```bash
python3 -m pgsa_cli.main --root . validate
python3 -m pgsa_cli.main --root . drift-report
```

