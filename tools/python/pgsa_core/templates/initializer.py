from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pgsa_core.io import append_jsonl, write_json
from pgsa_core.templates.defaults import (
    ADVANCED_DIRS,
    API_CONTRACT_TEMPLATE,
    INTEGRATION_REPORT_TEMPLATE,
    IMPORT_INDEX_TEMPLATE,
    PROJECT_TEMPLATE,
    REVIEW_TEMPLATE,
    SESSION_HARNESS_TEMPLATE,
    SESSION_SUMMARY_TEMPLATE,
    CAPABILITY_CONTRACT_TEMPLATE,
    COGNITIVE_AUDIT_NOTE_TEMPLATE,
    FACTORY_PLAN_TEMPLATE,
    REVIEW_ROUTER_TEMPLATE,
    RUNTIME_EVIDENCE_EVENT_TEMPLATE,
    SCENARIO_TEST_TEMPLATE,
    SESSION_RUNTIME_PROFILE_TEMPLATE,
    SIGNED_SKILL_MANIFEST_TEMPLATE,
    VERIFICATION_BLUEPRINT_TEMPLATE,
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
    "ledger/pending",
    "reports",
    "imports",
    "imports/inbox",
    "imports/sources",
]


def init_pgsa(root: Path, force: bool = False, advanced: bool = False) -> list[Path]:
    pgsa = root / "pgsa"
    written: list[Path] = []
    dirs = PGSA_DIRS + (ADVANCED_DIRS if advanced else [])
    for name in dirs:
        (pgsa / name).mkdir(parents=True, exist_ok=True)
    targets = {
        pgsa / "project.yaml": PROJECT_TEMPLATE,
        pgsa / "sessions.yaml": SESSIONS_TEMPLATE,
        pgsa / "contracts" / "api.project.v1.json": API_CONTRACT_TEMPLATE,
        pgsa / "integration" / "integration_report.json": INTEGRATION_REPORT_TEMPLATE,
        pgsa / "imports" / "index.json": IMPORT_INDEX_TEMPLATE,
    }
    if advanced:
        targets.update(
            {
                pgsa / "gates" / "verification_blueprint.yaml": VERIFICATION_BLUEPRINT_TEMPLATE,
                pgsa / "gates" / "review_router.yaml": REVIEW_ROUTER_TEMPLATE,
                pgsa / "runtime" / "session_runtime_profile.yaml": SESSION_RUNTIME_PROFILE_TEMPLATE,
                pgsa / "runtime" / "capability_contract.yaml": CAPABILITY_CONTRACT_TEMPLATE,
                pgsa / "skills" / "signed_skill_manifest.yaml": SIGNED_SKILL_MANIFEST_TEMPLATE,
                pgsa / "factory" / "factory_plan.yaml": FACTORY_PLAN_TEMPLATE,
                pgsa / "scenarios" / "project.acceptance.v1.yaml": SCENARIO_TEST_TEMPLATE,
            }
        )
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
        if force and ledger.exists():
            ledger.unlink()
        append_jsonl(
            ledger,
            {
                "event_id": "evt_000001",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "PGSA_INIT",
                "session": "system",
                "artifact_refs": ["project.yaml", "sessions.yaml"]
                + (["gates/verification_blueprint.yaml", "runtime/session_runtime_profile.yaml"] if advanced else []),
                "contract_refs": [],
                "merge_proposal_refs": [],
                "decision_refs": ["advanced scaffold" if advanced else "initial scaffold"],
                "status": "created",
            },
        )
        written.append(ledger)
    if advanced:
        runtime_evidence = pgsa / "evidence" / "runtime_evidence.jsonl"
        if force or not runtime_evidence.exists():
            if force and runtime_evidence.exists():
                runtime_evidence.unlink()
            append_jsonl(runtime_evidence, RUNTIME_EVIDENCE_EVENT_TEMPLATE)
            written.append(runtime_evidence)
        audit_note = pgsa / "audits" / "cognitive_audit_note.md"
        if force or not audit_note.exists():
            audit_note.write_text(COGNITIVE_AUDIT_NOTE_TEMPLATE, encoding="utf-8")
            written.append(audit_note)
    return written
