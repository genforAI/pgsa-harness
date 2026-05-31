from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pgsa_core.io import append_jsonl, read_jsonl, read_structured
from pgsa_core.metrics.drift import drift_report


def read_session_harness(root: Path, session: str) -> str:
    path = root / "pgsa" / "harness" / f"{session}.md"
    if not path.exists():
        raise FileNotFoundError(f"missing session harness: {path}")
    return path.read_text(encoding="utf-8")


def export_context(root: Path, session: str) -> str:
    pgsa = root / "pgsa"
    project = read_structured(pgsa / "project.yaml")
    sessions_doc = read_structured(pgsa / "sessions.yaml")
    sessions = sessions_doc.get("sessions", {})
    if session not in sessions:
        raise KeyError(f"unknown session: {session}")

    contract_summaries = []
    for contract in sorted((pgsa / "contracts").glob("*.json")):
        data = json.loads(contract.read_text(encoding="utf-8"))
        if session == data.get("owner_session") or session in data.get("consumer_sessions", []):
            contract_summaries.append(data)

    harness = read_session_harness(root, session)
    summary_path = pgsa / "state" / f"{session}.summary.md"
    summary = summary_path.read_text(encoding="utf-8") if summary_path.exists() else "(missing session summary)"
    latest_events = read_jsonl(pgsa / "ledger" / "coherence_ledger.jsonl")[-10:]
    report = drift_report(root)

    return f"""# PGSA Session Context

## Project

{project.get('project_name')} / `{project.get('project_id')}`

Goal: {project.get('goal')}

## Session Registration

```json
{json.dumps(sessions[session], indent=2, sort_keys=True)}
```

## Session Harness

{harness}

## Must Update

{chr(10).join(f"- {item}" for item in sessions[session].get('must_update', []))}

## Relevant Contracts

```json
{json.dumps(contract_summaries, indent=2, sort_keys=True)}
```

## Current Session Summary

{summary}

## Latest Ledger Events

```json
{json.dumps(latest_events, indent=2, sort_keys=True)}
```

## Current Drift Report

```json
{json.dumps(report, indent=2, sort_keys=True)}
```

## Required Completion Rule

Do not only say the project is coherent. Update the repo-local PGSA artifact that
makes the project state inspectable.
"""


def record_session_event(root: Path, session: str, event_type: str, status: str, artifact_refs: list[str] | None = None) -> None:
    ledger = root / "pgsa" / "ledger" / "coherence_ledger.jsonl"
    next_id = len(read_jsonl(ledger)) + 1
    append_jsonl(
        ledger,
        {
            "event_id": f"evt_{next_id:06d}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "session": session,
            "artifact_refs": artifact_refs or [],
            "status": status,
        },
    )


def continuation_prompt(root: Path, session: str) -> str:
    report = drift_report(root)
    return f"""# PGSA Continuation Prompt

Session: `{session}`

The current drift report still has unresolved work.

```json
{json.dumps(report, indent=2, sort_keys=True)}
```

Continue only inside your session scope unless a contract or integration issue
requires cross-session coordination. Update the session harness, session summary,
affected contracts, ledger, merge proposals, review, and integration artifacts as
needed.
"""
