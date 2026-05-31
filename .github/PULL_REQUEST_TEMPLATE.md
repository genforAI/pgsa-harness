## Summary

## PGSA artifacts affected

- [ ] contracts
- [ ] session summaries
- [ ] merge proposals
- [ ] reviews
- [ ] integration reports
- [ ] ledger events
- [ ] docs / templates / rules

## Validation

- [ ] `python3 -m unittest discover -s tools/python/tests -t tools/python`
- [ ] `PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard validate`
- [ ] `PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard drift-report`
- [ ] `python3 tools/scripts/validate_release.py --root .`

## Claim boundary

- [ ] This PR does not claim PGSA improves a commercial coding-agent product without Level 3 evidence.
