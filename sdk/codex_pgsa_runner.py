#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = REPO_ROOT / "tools" / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from pgsa_core.io import read_structured  # noqa: E402
from pgsa_core.supervisor.context import export_context  # noqa: E402


SANDBOX_NAMES = {
    "read_only": "read_only",
    "workspace_write": "workspace_write",
    "full_access": "full_access",
}


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def session_names(root: Path, configured: list[str] | None) -> list[str]:
    if configured:
        return configured
    sessions_doc = read_structured(root / "pgsa" / "sessions.yaml")
    return sorted(sessions_doc.get("sessions", {}))


def build_prompt(root: Path, session: str, task: str) -> str:
    context = export_context(root, session)
    return f"""{context}

## Codex SDK Task

{task}

## PGSA SDK Completion Rule

Before finishing, update this session's `must_update` artifacts or explicitly
explain which required update is blocked. If an imported harness or skill pack
changes project assumptions, update `pgsa/imports/index.json`, a contract, a
merge proposal, or a pending ledger event rather than relying on this thread's
chat history.
"""


def sandbox_value(name: str):
    from openai_codex import Sandbox

    mapping = {
        "read_only": Sandbox.read_only,
        "workspace_write": Sandbox.workspace_write,
        "full_access": Sandbox.full_access,
    }
    return mapping[name]


def run_real_codex(root: Path, config: dict[str, Any], prompts: dict[str, str]) -> int:
    try:
        from openai_codex import Codex
    except ImportError as exc:
        raise SystemExit(
            "Missing optional dependency `openai-codex`. Install with: pip install openai-codex"
        ) from exc

    model = config.get("model", "gpt-5.4")
    sandbox_name = config.get("sandbox", "workspace_write")
    ephemeral = config.get("ephemeral")
    if sandbox_name not in SANDBOX_NAMES:
        raise ValueError(f"unknown sandbox preset: {sandbox_name}")
    if ephemeral is not None and not isinstance(ephemeral, bool):
        raise ValueError("ephemeral must be a boolean when provided")

    with Codex() as codex:
        for session, prompt in prompts.items():
            thread = codex.thread_start(
                model=model,
                sandbox=sandbox_value(sandbox_name),
                cwd=str(root),
                ephemeral=ephemeral,
            )
            result = thread.run(prompt)
            print(json.dumps({"session": session, "thread_id": getattr(thread, "id", None), "ephemeral": ephemeral, "final_response": result.final_response}, indent=2))
    return 0


def start_only() -> int:
    try:
        from openai_codex import Codex
    except ImportError as exc:
        raise SystemExit(
            "Missing optional dependency `openai-codex`. Install with: pip install openai-codex"
        ) from exc

    with Codex() as codex:
        print(json.dumps({"codex_started": bool(codex)}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run PGSA-registered sessions through the optional Codex SDK.")
    parser.add_argument("--root", default=".", help="target project root containing pgsa/")
    parser.add_argument("--config", help="JSON config file")
    parser.add_argument("--session", action="append", help="session to run; may be repeated")
    parser.add_argument("--task", help="task override")
    parser.add_argument("--dry-run", action="store_true", help="print planned prompts without starting Codex")
    parser.add_argument("--start-only", action="store_true", help="start and stop the Codex SDK runtime without creating threads")
    args = parser.parse_args(argv)

    if args.start_only:
        return start_only()

    root = Path(args.root).resolve()
    config = load_config(Path(args.config)) if args.config else {}
    task = args.task or config.get(
        "task",
        "Continue the registered PGSA session work. Read PGSA context first and update required artifacts before handoff.",
    )
    sessions = session_names(root, args.session or config.get("sessions"))
    prompts = {session: build_prompt(root, session, task) for session in sessions}

    if args.dry_run:
        print(json.dumps({"root": str(root), "sessions": sessions, "prompts": prompts}, indent=2))
        return 0
    return run_real_codex(root, config, prompts)


if __name__ == "__main__":
    raise SystemExit(main())
