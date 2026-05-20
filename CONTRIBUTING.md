# Contributing to PGSA Harness Core

Thanks for considering a contribution.

PGSA Harness Core is an experimental repo-local project-coherence harness. Contributions should preserve the main boundary: this is a workflow layer around coding-agent sessions, not a product benchmark and not an internal modification of Codex, Claude Code, or Grok Build.

## Good contribution areas

- Clearer PGSA artifact templates.
- Better Codex / Claude Code / generic adapter examples.
- Lifecycle supervisor improvements.
- More precise validators.
- Example projects showing contract drift, semantic merge, review gates, and integration readiness.
- Documentation that helps users adopt PGSA in a real repository.

## Before submitting

1. Run the smoke tests:

```bash
python3 -m unittest discover -s tests -t .
```

2. Validate the example project:

```bash
python3 -m pgsa_cli.main --root examples/teamtask-projectboard validate
python3 -m pgsa_cli.main --root examples/teamtask-projectboard drift-report
```

3. Do not add product-level claims unless real Level 3 transcripts and evidence exist.
