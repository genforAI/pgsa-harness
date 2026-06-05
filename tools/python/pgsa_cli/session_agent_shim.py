from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pgsa_cli import cli as base
from pgsa_core.io import read_structured, write_json
from pgsa_core.supervisor.context import record_session_event


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "-", value.strip()).strip("-") or "session"


def _relpath(target: Path, start: Path) -> str:
    return Path(os.path.relpath(target, start)).as_posix()


def _project_relative(path: Path, root: Path) -> str:
    return Path(os.path.relpath(path, root)).as_posix()


def _session_doc(pgsa: Path, session_id: str) -> dict[str, Any]:
    sessions_path = pgsa / "sessions.yaml"
    if not sessions_path.exists():
        raise FileNotFoundError(f"missing sessions file: {sessions_path}")
    sessions_doc = read_structured(sessions_path)
    sessions = sessions_doc.get("sessions", {})
    if not isinstance(sessions, dict):
        raise ValueError(f"sessions field should be an object: {sessions_path}")
    if session_id not in sessions:
        raise KeyError(f"unknown session: {session_id}; register it before creating a session agent folder")
    session = sessions[session_id]
    if not isinstance(session, dict):
        raise ValueError(f"session entry should be an object: {session_id}")
    return session


def _text_list(values: Any) -> str:
    if isinstance(values, list) and values:
        return "\n".join(f"- `{item}`" for item in values)
    return "- none"


def _agent_markdown(*, session_id: str, session: dict[str, Any]) -> str:
    role = session.get("role", "project-session")
    return f"""# PGSA Session Agent: {session_id}

This folder is a launch wrapper for one registered PGSA session. The semantic
source of truth remains `pgsa/sessions.yaml`; this file only tells a fresh
Codex, Claude Code, or SDK-launched agent how to attach itself to that
registration.

## Startup

1. Read `./PGSA_SESSION.json`.
2. Resolve `pgsa_root` and `harness_root` relative to this file.
3. Read `<harness_root>/protocol/SKILL.md`.
4. Read `<pgsa_root>/sessions.yaml`.
5. Read `<pgsa_root>/harness/{session_id}.md`.
6. Read `<pgsa_root>/state/{session_id}.summary.md`.
7. Read every `must_read` artifact declared below.
8. Read `<pgsa_root>/skills/signed_skill_manifest.yaml` if present, and use
   only entries whose `applies_to` contains `{session_id}` or `*`.
9. Do not read or apply raw `<pgsa_root>/imports/sources/<source_id>/` content
   unless this session is `external_import_review` or the source is explicitly
   listed in this session's `must_read`.
10. Before handoff, update every applicable `must_update` artifact and write a
    pending ledger event if the session changed project assumptions.

## Registered Role

- session: `{session_id}`
- role: `{role}`

## Owner Scope

{_text_list(session.get("owner_scope"))}

## Must Read

{_text_list(session.get("must_read"))}

## Must Update

{_text_list(session.get("must_update"))}

## Boundary

This session folder does not grant file access, sandbox permissions, merge
authority, or global skill authority. It only binds the running agent to a PGSA
session identity and the reviewed artifacts that identity is allowed to use.
"""


def _skill_markdown(*, session_id: str, session: dict[str, Any]) -> str:
    role = session.get("role", "project-session")
    safe_session = _safe_name(session_id)
    return f"""---
name: pgsa-session-{safe_session}
description: Use when launching the `{session_id}` PGSA session from this folder.
---

# PGSA Session Skill: {session_id}

Follow `AGENTS.md` in this folder. This skill is a local launch aid for the
registered `{session_id}` session (`{role}`); it does not replace
`pgsa/sessions.yaml` or activate unreviewed imported skills.
"""


def cmd_session_agent_create(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    pgsa = root / "pgsa"
    session = _session_doc(pgsa, args.session)

    if args.out:
        output_dir = Path(args.out)
        if not output_dir.is_absolute():
            output_dir = root / output_dir
    else:
        output_dir = pgsa / "session_agents" / args.session
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.harness_root:
        harness_root = Path(args.harness_root)
        if not harness_root.is_absolute():
            harness_root = root / harness_root
    else:
        harness_root = root / "pgsa-harness"
    harness_root = harness_root.resolve()

    descriptor = {
        "session_id": args.session,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pgsa_root": _relpath(pgsa, output_dir),
        "harness_root": _relpath(harness_root, output_dir),
        "session_registry": _relpath(pgsa / "sessions.yaml", output_dir),
        "session_harness": _relpath(pgsa / "harness" / f"{args.session}.md", output_dir),
        "session_summary": _relpath(pgsa / "state" / f"{args.session}.summary.md", output_dir),
        "accepted_skills_manifest": _relpath(pgsa / "skills" / "signed_skill_manifest.yaml", output_dir),
        "raw_import_sources_policy": "do_not_read_unless_external_import_review_or_explicit_must_read",
        "role": session.get("role"),
        "owner_scope": session.get("owner_scope", []),
        "must_read": session.get("must_read", []),
        "must_update": session.get("must_update", []),
        "handoff_to": session.get("handoff_to", []),
    }
    write_json(output_dir / "PGSA_SESSION.json", descriptor)
    (output_dir / "AGENTS.md").write_text(_agent_markdown(session_id=args.session, session=session), encoding="utf-8")
    (output_dir / "SKILL.md").write_text(_skill_markdown(session_id=args.session, session=session), encoding="utf-8")

    artifacts = [
        _project_relative(output_dir / "PGSA_SESSION.json", root),
        _project_relative(output_dir / "AGENTS.md", root),
        _project_relative(output_dir / "SKILL.md", root),
    ]
    record_session_event(root, args.session, "SESSION_AGENT_FOLDER_CREATED", "created", artifacts)
    print(
        base.json.dumps(
            {
                "session": args.session,
                "agent_dir": str(output_dir),
                "pgsa_root": descriptor["pgsa_root"],
                "harness_root": descriptor["harness_root"],
                "artifacts": artifacts,
            },
            indent=2,
        )
    )
    return 0


def _add_session_agent_parser(parser: argparse.ArgumentParser) -> None:
    subparsers = next(
        action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
    )
    if "session-agent" in subparsers.choices:
        return
    session_agent = subparsers.add_parser("session-agent")
    session_agent_sub = session_agent.add_subparsers(dest="session_agent_command", required=True)

    create = session_agent_sub.add_parser("create")
    create.add_argument("session")
    create.add_argument(
        "--out",
        default=None,
        help="output directory; relative paths are resolved from --root (default: pgsa/session_agents/<session>)",
    )
    create.add_argument(
        "--harness-root",
        default=None,
        help="PGSA harness checkout path; relative paths are resolved from --root (default: pgsa-harness)",
    )
    create.set_defaults(func=cmd_session_agent_create)


def install() -> None:
    original = base.build_parser

    if getattr(original, "_pgsa_session_agent_shim_installed", False):
        return

    def wrapped_build_parser() -> argparse.ArgumentParser:
        parser = original()
        _add_session_agent_parser(parser)
        return parser

    wrapped_build_parser._pgsa_session_agent_shim_installed = True  # type: ignore[attr-defined]
    base.build_parser = wrapped_build_parser
