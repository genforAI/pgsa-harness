from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pgsa_core.io import read_jsonl, read_structured


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


def _artifact_exists(pgsa: Path, rel: str) -> bool:
    path = pgsa / rel
    if rel.endswith("/"):
        return path.is_dir()
    if "*" in rel:
        return bool(list(pgsa.glob(rel)))
    return path.exists()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _markdown_field(text: str, field: str) -> str:
    prefix = f"{field.lower()}:"
    for line in text.splitlines():
        normalized = line.strip().lower()
        if normalized.startswith(prefix):
            return line.split(":", 1)[1].strip().lower()
    if field.lower() == "status":
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if line.strip().lower() == "## status" and index + 1 < len(lines):
                return lines[index + 1].strip().lower()
    return ""


def _markdown_items(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return []
    value = value.strip("[]")
    return [
        item.strip().strip("'\"")
        for item in re.split(r"[, ]+", value)
        if item.strip().strip("'\"")
    ]


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
    session_names = set(sessions)
    for session, data in sessions.items():
        harness = pgsa / "harness" / f"{session}.md"
        if not harness.exists():
            issues.append(_issue("artifact_completeness", "warning", f"{session} missing session harness", harness))
        for field in ["role", "status", "owner_scope", "produces", "consumes", "must_read", "must_update", "handoff_to"]:
            if field not in data:
                issues.append(_issue("artifact_completeness", "warning", f"{session} missing session field {field}", pgsa / "sessions.yaml"))
        for field in ["owner_scope", "produces", "consumes", "must_read", "must_update", "handoff_to"]:
            if field in data and not isinstance(data[field], list):
                issues.append(_issue("artifact_completeness", "warning", f"{session} field {field} should be a list", pgsa / "sessions.yaml"))
        for target in _as_list(data.get("handoff_to")):
            if target not in session_names:
                issues.append(_issue("artifact_completeness", "error", f"{session} handoff target unknown session {target}", pgsa / "sessions.yaml"))
        for field in ["consumes", "must_read", "must_update"]:
            for rel in _as_list(data.get(field)):
                if not isinstance(rel, str):
                    issues.append(_issue("artifact_completeness", "warning", f"{session} field {field} contains non-string artifact", pgsa / "sessions.yaml"))
                    continue
                if not _artifact_exists(pgsa, rel):
                    issues.append(_issue("artifact_completeness", "warning", f"{session} missing {field} artifact {rel}", pgsa / rel))
    for contract in (pgsa / "contracts").glob("*.json"):
        try:
            data = json.loads(contract.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(_issue("contract_violations", "error", f"invalid contract JSON: {exc}", contract))
            continue
        for field in [
            "contract_id",
            "owner_session",
            "producer_session",
            "consumer_sessions",
            "boundary_type",
            "requires_review",
            "review_state",
        ]:
            if field not in data:
                issues.append(_issue("contract_violations", "error", f"contract missing {field}", contract))
        if data.get("owner_session") not in sessions:
            issues.append(_issue("contract_violations", "error", f"unknown owner session {data.get('owner_session')}", contract))
        if data.get("producer_session") not in sessions:
            issues.append(_issue("contract_violations", "error", f"unknown producer session {data.get('producer_session')}", contract))
        for session in _as_list(data.get("consumer_sessions")):
            if session not in sessions:
                issues.append(_issue("contract_violations", "error", f"unknown consumer session {session}", contract))
        review_state = data.get("review_state", {})
        for session in _as_list(data.get("requires_review")):
            if session not in sessions:
                issues.append(_issue("contract_violations", "error", f"unknown review session {session}", contract))
            state = str(review_state.get(session, "")).lower()
            if not state:
                issues.append(_issue("review_debt_items", "warning", f"missing review state for {session}", contract))
            elif state in {"blocking", "rejected"}:
                issues.append(_issue("integration_failures", "error", f"contract review blocked by {session}", contract))
            elif state not in {"accepted", "not_required"}:
                issues.append(_issue("review_debt_items", "warning", f"contract review not accepted by {session}: {state}", contract))
        if data.get("breaking_change") and not data.get("open_merge_proposals"):
            issues.append(_issue("review_debt_items", "warning", "breaking contract change has no open merge proposal reference", contract))
        for proposal_ref in _as_list(data.get("open_merge_proposals")):
            if isinstance(proposal_ref, str) and proposal_ref and not _artifact_exists(pgsa, proposal_ref):
                issues.append(_issue("contract_violations", "error", f"open merge proposal reference not found: {proposal_ref}", contract))
    integration = pgsa / "integration" / "integration_report.json"
    if integration.exists():
        try:
            report = json.loads(integration.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(_issue("integration_failures", "error", f"invalid integration report: {exc}", integration))
            report = {}
        if report.get("blocking_issues"):
            issues.append(_issue("integration_failures", "error", "integration report has blocking issues", integration))
        if report.get("open_merge_proposals"):
            issues.append(_issue("integration_failures", "error", "integration report has open merge proposals", integration))
        for session, state in report.get("session_readiness", {}).items():
            if session not in sessions:
                issues.append(_issue("integration_failures", "error", f"integration report references unknown session {session}", integration))
            elif str(state).lower() in {"blocked", "not_ready", "failing"}:
                issues.append(_issue("integration_failures", "error", f"session {session} is not integration-ready", integration))
        for contract_id, state in report.get("contract_review_state", {}).items():
            if str(state).lower() in {"blocking", "rejected"}:
                issues.append(_issue("integration_failures", "error", f"contract {contract_id} review is blocking", integration))
            elif str(state).lower() not in {"accepted", "not_required"}:
                issues.append(_issue("review_debt_items", "warning", f"contract {contract_id} review state is {state}", integration))
    ledger = pgsa / "ledger" / "coherence_ledger.jsonl"
    events = read_jsonl(ledger)
    if not events:
        issues.append(_issue("stale_state_items", "warning", "coherence ledger has no events", ledger))
    for event in events:
        for field in ["event_id", "timestamp", "session", "event_type", "status"]:
            if field not in event:
                issues.append(_issue("stale_state_items", "warning", f"ledger event missing {field}", ledger))
        if event.get("session") not in sessions and event.get("session") != "system":
            issues.append(_issue("stale_state_items", "warning", f"ledger event references unknown session {event.get('session')}", ledger))
    for pending in (pgsa / "ledger" / "pending").glob("*.json"):
        try:
            event = json.loads(pending.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(_issue("stale_state_items", "error", f"invalid pending ledger event: {exc}", pending))
            continue
        for field in ["event_id", "timestamp", "session", "event_type", "status"]:
            if field not in event:
                issues.append(_issue("stale_state_items", "warning", f"pending ledger event missing {field}", pending))
        if event.get("session") not in sessions and event.get("session") != "system":
            issues.append(_issue("stale_state_items", "warning", f"pending ledger event references unknown session {event.get('session')}", pending))
    for proposal in (pgsa / "merge_proposals").glob("*.md"):
        text = proposal.read_text(encoding="utf-8").lower()
        status = _markdown_field(text, "status")
        if status not in {"resolved", "closed", "accepted"}:
            issues.append(_issue("unresolved_merge_conflicts", "warning", "unresolved merge proposal", proposal))
        for field in ["decision_owner", "producer_session", "consumer_sessions", "changed_contracts"]:
            if not _markdown_field(text, field):
                issues.append(_issue("review_debt_items", "warning", f"merge proposal missing {field}", proposal))
        decision_owner = _markdown_field(text, "decision_owner")
        if decision_owner and decision_owner not in sessions:
            issues.append(_issue("review_debt_items", "warning", f"merge proposal decision owner unknown session {decision_owner}", proposal))
        producer_session = _markdown_field(text, "producer_session")
        if producer_session and producer_session not in sessions:
            issues.append(_issue("review_debt_items", "warning", f"merge proposal producer unknown session {producer_session}", proposal))
        for consumer_session in _markdown_items(_markdown_field(text, "consumer_sessions")):
            if consumer_session not in sessions:
                issues.append(_issue("review_debt_items", "warning", f"merge proposal consumer unknown session {consumer_session}", proposal))
    _validate_advanced_artifacts(pgsa, sessions, issues)
    return issues


def _read_optional_structured(path: Path, issues: list[ValidationIssue], category: str) -> Any | None:
    if not path.exists():
        return None
    try:
        return read_structured(path)
    except Exception as exc:
        issues.append(_issue(category, "error", f"invalid structured advanced artifact: {exc}", path))
        return None


def _validate_advanced_artifacts(pgsa: Path, sessions: dict[str, Any], issues: list[ValidationIssue]) -> None:
    session_names = set(sessions)
    category = "advanced_capability_state"

    blueprint = _read_optional_structured(pgsa / "gates" / "verification_blueprint.yaml", issues, category)
    if blueprint is not None:
        for field in ["blueprint_id", "status", "contract_refs", "required_checks", "gate_policy"]:
            if field not in blueprint:
                issues.append(_issue(category, "warning", f"verification blueprint missing {field}", pgsa / "gates" / "verification_blueprint.yaml"))
        for check in _as_list(blueprint.get("required_checks")):
            if not isinstance(check, dict):
                issues.append(_issue(category, "warning", "verification blueprint check should be an object", pgsa / "gates" / "verification_blueprint.yaml"))
                continue
            if check.get("owner_session") not in session_names:
                issues.append(_issue(category, "warning", f"verification check owner session unknown: {check.get('owner_session')}", pgsa / "gates" / "verification_blueprint.yaml"))

    router = _read_optional_structured(pgsa / "gates" / "review_router.yaml", issues, category)
    if router is not None:
        for field in ["router_id", "risk_tiers", "routing_rules"]:
            if field not in router:
                issues.append(_issue(category, "warning", f"review router missing {field}", pgsa / "gates" / "review_router.yaml"))
        for rule in _as_list(router.get("routing_rules")):
            if not isinstance(rule, dict) or not rule.get("route"):
                issues.append(_issue(category, "warning", "review router rule missing route", pgsa / "gates" / "review_router.yaml"))

    runtime_profile = _read_optional_structured(pgsa / "runtime" / "session_runtime_profile.yaml", issues, category)
    if runtime_profile is not None:
        profiles = runtime_profile.get("profiles", {})
        if not isinstance(profiles, dict) or not profiles:
            issues.append(_issue(category, "warning", "runtime profile has no profiles", pgsa / "runtime" / "session_runtime_profile.yaml"))
        for session, profile in profiles.items():
            if session not in session_names:
                issues.append(_issue(category, "warning", f"runtime profile references unknown session {session}", pgsa / "runtime" / "session_runtime_profile.yaml"))
            if isinstance(profile, dict):
                for field in ["allowed", "denied", "requires_approval", "evidence_outputs"]:
                    if field not in profile:
                        issues.append(_issue(category, "warning", f"runtime profile {session} missing {field}", pgsa / "runtime" / "session_runtime_profile.yaml"))

    capability = _read_optional_structured(pgsa / "runtime" / "capability_contract.yaml", issues, category)
    if capability is not None:
        contracts = capability.get("contracts", {})
        if not isinstance(contracts, dict) or not contracts:
            issues.append(_issue(category, "warning", "capability contract has no session contracts", pgsa / "runtime" / "capability_contract.yaml"))
        for session in contracts:
            if session not in session_names:
                issues.append(_issue(category, "warning", f"capability contract references unknown session {session}", pgsa / "runtime" / "capability_contract.yaml"))

    skills = _read_optional_structured(pgsa / "skills" / "signed_skill_manifest.yaml", issues, category)
    if skills is not None:
        for skill in _as_list(skills.get("skills")):
            if not isinstance(skill, dict):
                issues.append(_issue(category, "warning", "skill manifest entry should be an object", pgsa / "skills" / "signed_skill_manifest.yaml"))
                continue
            for field in ["skill_id", "version", "status", "applies_to", "signed_by"]:
                if field not in skill:
                    issues.append(_issue(category, "warning", f"skill manifest entry missing {field}", pgsa / "skills" / "signed_skill_manifest.yaml"))
            for session in _as_list(skill.get("applies_to")):
                if session not in session_names:
                    issues.append(_issue(category, "warning", f"skill applies to unknown session {session}", pgsa / "skills" / "signed_skill_manifest.yaml"))

    factory = _read_optional_structured(pgsa / "factory" / "factory_plan.yaml", issues, category)
    if factory is not None:
        task_ids = {task.get("task_id") for task in _as_list(factory.get("tasks")) if isinstance(task, dict)}
        for task in _as_list(factory.get("tasks")):
            if not isinstance(task, dict):
                issues.append(_issue(category, "warning", "factory task should be an object", pgsa / "factory" / "factory_plan.yaml"))
                continue
            if task.get("session") not in session_names:
                issues.append(_issue(category, "warning", f"factory task references unknown session {task.get('session')}", pgsa / "factory" / "factory_plan.yaml"))
            for dep in _as_list(task.get("depends_on")):
                if dep not in task_ids:
                    issues.append(_issue(category, "warning", f"factory task dependency unknown: {dep}", pgsa / "factory" / "factory_plan.yaml"))

    for scenario in (pgsa / "scenarios").glob("*.yaml"):
        data = _read_optional_structured(scenario, issues, category)
        if data is None:
            continue
        for field in ["scenario_id", "owner_session", "contract_refs", "steps", "expected_evidence"]:
            if field not in data:
                issues.append(_issue(category, "warning", f"scenario test missing {field}", scenario))
        if data.get("owner_session") not in session_names:
            issues.append(_issue(category, "warning", f"scenario owner session unknown: {data.get('owner_session')}", scenario))

    for event in read_jsonl(pgsa / "evidence" / "runtime_evidence.jsonl"):
        for field in ["event_id", "timestamp", "session", "event_type", "status", "evidence_ref"]:
            if field not in event:
                issues.append(_issue(category, "warning", f"runtime evidence event missing {field}", pgsa / "evidence" / "runtime_evidence.jsonl"))
        if event.get("session") not in session_names and event.get("session") != "system":
            issues.append(_issue(category, "warning", f"runtime evidence references unknown session {event.get('session')}", pgsa / "evidence" / "runtime_evidence.jsonl"))


def issues_to_dicts(issues: list[ValidationIssue]) -> list[dict[str, str]]:
    return [issue.__dict__ for issue in issues]
