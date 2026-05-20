from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from core.io import append_jsonl, write_json
from core.templates.defaults import (
    API_CONTRACT_TEMPLATE,
    INTEGRATION_REPORT_TEMPLATE,
    PROJECT_TEMPLATE,
    REVIEW_TEMPLATE,
    SESSION_HARNESS_TEMPLATE,
    SESSION_SUMMARY_TEMPLATE,
    SESSIONS_TEMPLATE,
)


PGSA_DIRS = [
    "contracts",
    "harness",
    "state",
    "merge_proposals",
    "reviews",
    "integration",
    "ledger",
    "reports",
]


def init_pgsa(root: Path, force: bool = False) -> list[Path]:
    pgsa = root / "pgsa"
    written: list[Path] = []
    for name in PGSA_DIRS:
        (pgsa / name).mkdir(parents=True, exist_ok=True)
    targets = {
        pgsa / "project.yaml": PROJECT_TEMPLATE,
        pgsa / "sessions.yaml": SESSIONS_TEMPLATE,
        pgsa / "contracts" / "api.project.v1.json": API_CONTRACT_TEMPLATE,
        pgsa / "integration" / "integration_report.json": INTEGRATION_REPORT_TEMPLATE,
    }
    for path, data in targets.items():
        if force or not path.exists():
            write_json(path, data)
            written.append(path)
    sessions = SESSIONS_TEMPLATE["sessions"]
    for session, data in sessions.items():
        scope = "\n".join(f"- {item}" for item in data["owner_scope"])
        summary = pgsa / "state" / f"{session}.summary.md"
        if force or not summary.exists():
            summary.write_text(SESSION_SUMMARY_TEMPLATE.format(session=session, scope=scope), encoding="utf-8")
            written.append(summary)
        harness = pgsa / "harness" / f"{session}.md"
        if force or not harness.exists():
            harness.write_text(SESSION_HARNESS_TEMPLATE.format(session=session, scope=scope), encoding="utf-8")
            written.append(harness)
    reviews = {
        "frontend_components_review.md": "Frontend Components Review",
        "security_review.md": "Security Review",
    }
    for filename, title in reviews.items():
        path = pgsa / "reviews" / filename
        if force or not path.exists():
            path.write_text(REVIEW_TEMPLATE.format(name=title), encoding="utf-8")
            written.append(path)
    ledger = pgsa / "ledger" / "coherence_ledger.jsonl"
    if force or not ledger.exists():
        append_jsonl(
            ledger,
            {
                "event_id": "evt_000001",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "PGSA_INIT",
                "session": "system",
                "artifact_refs": ["project.yaml", "sessions.yaml"],
                "status": "created",
            },
        )
        written.append(ledger)
    return written
