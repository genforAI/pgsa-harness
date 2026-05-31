# Contributing to PGSA Harness Core

Thanks for considering a contribution.

PGSA Harness Core is a repo-local project-coherence protocol.
Contributions should preserve the main boundary: the agent-facing product
surface is `protocol/` plus generated `pgsa/` artifacts, not optional tooling or
product benchmark claims.

## Good contribution areas

- Clearer PGSA artifact templates and schemas.
- Sharper agent workflow rules in `protocol/SKILL.md`.
- More precise optional validators.
- Example projects showing contract drift, semantic merge, review gates, and integration readiness.
- Documentation that helps users adopt PGSA in a real repository.

## Before submitting

1. Run the smoke tests:

```bash
python3 -m unittest discover -s tools/python/tests -t tools/python
```

2. Validate the example project:

```bash
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard validate
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard drift-report
```

3. Do not add product-level claims unless real Level 3 transcripts and evidence exist.
