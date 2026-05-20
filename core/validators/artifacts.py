from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.io import read_jsonl, read_structured


@dataclass
class ValidationIssue:
    category: str
    severity: str
    message: str
    path: str


def _issue(category: str, severity: str, message: str, path: Path) -> ValidationIssue:
    return ValidationIssue(category=category, severity=severity, message=message, path=str(path))


def load_project(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    pgsa = root / "pgsa"
    return read_structured(pgsa / "project.yaml"), read_structured(pgsa / "sessions.yaml")


def validate(root: Path) -> list[ValidationIssue]:
    pgsa = root / "pgsa"
    issues: list[ValidationIssue] = []
    if not pgsa.exists():
        return [_issue("artifact_completeness", "error", "missing pgsa/ directory", pgsa)]
    required_dirs = ["contracts", "harness", "state", "merge_proposals", "reviews", "integration", "ledger", "reports"]
    for name in required_dirs:
        path = pgsa / name
        if not path.exists():
            issues.append(_issue("artifact_completeness", "error", f"missing pgsa/{name}/", path))
    for name in ["project.yaml", "sessions.yaml"]:
        path = pgsa / name
        if not path.exists():
            issues.append(_issue("artifact_completeness", "error", f"missing {name}", path))
        else:
            try:
                read_structured(path)
            except Exception as exc:
                issues.append(_issue("artifact_completeness", "error", f"invalid structured file: {exc}", path))
    if any(i.severity == "error" for i in issues):
        return issues
    _project, sessions_doc = load_project(root)
    sessions = sessions_doc.get("sessions", {})
    for session, data in sessions.items():
        harness = pgsa / "harness" / f"{session}.md"
        if not harness.exists():
            issues.append(_issue("artifact_completeness", "warning", f"{session} missing session harness", harness))
        for rel in data.get("must_update", []):
            if "*" in rel:
                parent = pgsa / rel.split("*", 1)[0]
                if not list(parent.parent.glob(parent.name + "*")):
                    issues.append(_issue("artifact_completeness", "warning", f"{session} has no artifact matching {rel}", pgsa / rel))
            else:
                path = pgsa / rel
                if not path.exists():
                    issues.append(_issue("artifact_completeness", "warning", f"{session} missing required artifact {rel}", path))
    for contract in (pgsa / "contracts").glob("*.json"):
        try:
            data = json.loads(contract.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(_issue("contract_violations", "error", f"invalid contract JSON: {exc}", contract))
            continue
        for field in ["contract_id", "owner_session", "consumer_sessions", "response_shape", "requires_review"]:
            if field not in data:
                issues.append(_issue("contract_violations", "error", f"contract missing {field}", contract))
        for session in data.get("consumer_sessions", []):
            if session not in sessions:
                issues.append(_issue("contract_violations", "error", f"unknown consumer session {session}", contract))
    integration = pgsa / "integration" / "integration_report.json"
    if integration.exists():
        try:
            report = json.loads(integration.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(_issue("integration_failures", "error", f"invalid integration report: {exc}", integration))
            report = {}
        if report.get("blocking_issues"):
            issues.append(_issue("integration_failures", "error", "integration report has blocking issues", integration))
    ledger = pgsa / "ledger" / "coherence_ledger.jsonl"
    events = read_jsonl(ledger)
    if not events:
        issues.append(_issue("stale_state_items", "warning", "coherence ledger has no events", ledger))
    for proposal in (pgsa / "merge_proposals").glob("*.md"):
        text = proposal.read_text(encoding="utf-8").lower()
        if "status: resolved" not in text:
            issues.append(_issue("unresolved_merge_conflicts", "warning", "unresolved merge proposal", proposal))
    return issues


def issues_to_dicts(issues: list[ValidationIssue]) -> list[dict[str, str]]:
    return [issue.__dict__ for issue in issues]
