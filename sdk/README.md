# PGSA Optional Codex SDK Demo

This folder is an optional demo layer. PGSA core remains the repo-local file
protocol under `protocol/`; this demo is for users who already want to use the
Codex SDK to drive multiple PGSA-registered sessions. It is not part of PGSA
core and does not imply OpenAI/Codex endorsement or official integration.

The official Python SDK controls the local Codex app-server over JSON-RPC and
is installed separately:

```bash
pip install openai-codex
```

The demo runner reads `pgsa/sessions.yaml`, builds one PGSA-aware prompt per
session, and either prints the plan (`--dry-run`) or starts Codex SDK threads in
the target project root passed by `--root`.

```bash
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json --dry-run
```

To verify the installed SDK runtime without sending a model prompt:

```bash
python3 sdk/codex_pgsa_runner.py --start-only
```

For a real SDK run:

```bash
pip install openai-codex
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json
```

Set `"ephemeral": true` in the config for temporary verification runs that
should not keep long-lived Codex thread history. Leave it `false` when you want
the SDK-run sessions to remain resumable.

Keep this as userland orchestration:

- it does not change PGSA protocol semantics;
- it does not make external imports trusted automatically;
- it does not replace Codex sandboxing or approvals;
- it should write project state through the normal PGSA artifacts.
