# OpenCode / Generic Agent Notes

Use this folder for OpenCode-style or other generic agent workflows.

PGSA does not require private product APIs. A generic agent can use:

```bash
python3 -m pgsa_cli.main --root . export-context --session backend --output .pgsa_context.md
```

Then the agent reads `.pgsa_context.md`, performs the task, updates the
repo-local `pgsa/` artifacts, and runs:

```bash
python3 -m pgsa_cli.main --root . validate
python3 -m pgsa_cli.main --root . drift-report
```

