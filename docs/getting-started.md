# Getting Started

PGSA Harness Core is a repo-local project-coherence protocol for coding-agent
workflows.

## Initialize A Project

```bash
mkdir demo-project
python -m pgsa_cli.main --root demo-project init
python -m pgsa_cli.main --root demo-project validate
python -m pgsa_cli.main --root demo-project drift-report
```

Use `python3` if your system does not provide `python`.

## Read A Session Harness

```bash
python -m pgsa_cli.main --root demo-project harness --session backend
```

## Export Context For An Agent

```bash
python -m pgsa_cli.main --root demo-project export-context --session backend --output backend_context.md
```

The exported context is a convenience packet. The source of truth remains the
repo-local `pgsa/` files.
