from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pgsa_core.io import read_jsonl, read_structured

ARTIFACT_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")
EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
RISK_LEVELS = {"low", "medium", "high", "critical"}
EVIDENCE_STATUSES = {"allowed", "denied", "blocked", "observed", "passed", "failed", "warning"}
DEFAULT_POSTURES = {"least_privilege", "read_only", "review_required", "manual_approval"}


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


def _looks_like_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ARTIFACT_ID_RE.match(value))


def _looks_like_event_type(value: Any) -> bool:
    return isinstance(value, str) and bool(EVENT_TYPE_RE.match(value))


def _valid_rel_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if value.startswith(("/", "~")):
        return False
    parts = [part for part in value.replace("\\", "/").split("/") if part]
    return ".." not in parts


def _warn_if_bad_id(issues: list[ValidationIssue], category: str, path: Path, field: str, value: Any) -> None:
    if not _looks_like_id(value):
        issues.append(_issue(category, "warning", f"{field} should be a stable artifact id", path))


def _warn_if_bad_rel_path(issues: list[ValidationIssue], category: str, path: Path, field: str, value: Any) -> None:
    if not _valid_rel_path(value):
        issues.append(_issue(category, "warning", f"{field} should be a relative project artifact path", path))


def _warn_if_bad_enum(
    issues: list[ValidationIssue],
    category: str,
    path: Path,
    field: str,
    value: Any,
    allowed: set[str],
) -> None:
    if not isinstance(value, str) or value.lower() not in allowed:
        issues.append(_issue(category, "warning", f"{field} should be one of {sorted(allowed)}", path))


def _duplicate_values(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value:
            continue
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _append_duplicate_id_issues(
    issues: list[ValidationIssue],
    category: str,
    path: Path,
    field: str,
    values: list[Any],
) -> None:
    for duplicate in _duplicate_values(values):
        issues.append(_issue(category, "warning", f"duplicate {field}: {duplicate}", path))


def _factory_plan_has_cycle(tasks: list[dict[str, Any]]) -> bool:
    graph = {
        task.get("task_id"): [dep for dep in _as_list(task.get("depends_on")) if isinstance(dep, str)]
        for task in tasks
        if isinstance(task.get("task_id"), str)
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> bool:
        if task_id in visiting:
            return True
        if task_id in visited:
            return False
        visiting.add(task_id)
        for dep in graph.get(task_id, []):
            if dep in graph and visit(dep):
                return True
        visiting.remove(task_id)
        visited.add(task_id)
        return False

    return any(visit(task_id) for task_id in list(graph))


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return None


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
        blueprint_path = pgsa / "gates" / "verification_blueprint.yaml"
        _warn_if_bad_id(issues, category, blueprint_path, "blueprint_id", blueprint.get("blueprint_id"))
        _warn_if_bad_enum(issues, category, blueprint_path, "status", blueprint.get("status"), {"draft", "active", "deprecated"})
        for field in ["blueprint_id", "status", "contract_refs", "required_checks", "gate_policy"]:
            if field not in blueprint:
                issues.append(_issue(category, "warning", f"verification blueprint missing {field}", blueprint_path))
        for contract_ref in _as_list(blueprint.get("contract_refs")):
            if not isinstance(contract_ref, str) or not contract_ref:
                issues.append(_issue(category, "warning", "verification blueprint contract_refs should be non-empty strings", blueprint_path))
        for check in _as_list(blueprint.get("required_checks")):
            if not isinstance(check, dict):
                issues.append(_issue(category, "warning", "verification blueprint check should be an object", blueprint_path))
                continue
            _warn_if_bad_id(issues, category, blueprint_path, "verification check_id", check.get("check_id"))
            if "evidence" in check:
                _warn_if_bad_rel_path(issues, category, blueprint_path, "verification evidence", check.get("evidence"))
            if check.get("owner_session") not in session_names:
                issues.append(_issue(category, "warning", f"verification check owner session unknown: {check.get('owner_session')}", blueprint_path))
        _append_duplicate_id_issues(
            issues,
            category,
            blueprint_path,
            "verification check_id",
            [check.get("check_id") for check in _as_list(blueprint.get("required_checks")) if isinstance(check, dict)],
        )

    router = _read_optional_structured(pgsa / "gates" / "review_router.yaml", issues, category)
    if router is not None:
        router_path = pgsa / "gates" / "review_router.yaml"
        _warn_if_bad_id(issues, category, router_path, "router_id", router.get("router_id"))
        risk_tiers = router.get("risk_tiers", {})
        if isinstance(risk_tiers, dict):
            for risk in risk_tiers:
                if risk not in RISK_LEVELS:
                    issues.append(_issue(category, "warning", f"review router has unknown risk tier {risk}", router_path))
        for field in ["router_id", "risk_tiers", "routing_rules"]:
            if field not in router:
                issues.append(_issue(category, "warning", f"review router missing {field}", router_path))
        for rule in _as_list(router.get("routing_rules")):
            if not isinstance(rule, dict) or not rule.get("route"):
                issues.append(_issue(category, "warning", "review router rule missing route", router_path))
                continue
            _warn_if_bad_id(issues, category, router_path, "review router rule_id", rule.get("rule_id"))
            if "blocking" in rule and not isinstance(rule.get("blocking"), bool):
                issues.append(_issue(category, "warning", "review router blocking should be boolean", router_path))

    runtime_profile = _read_optional_structured(pgsa / "runtime" / "session_runtime_profile.yaml", issues, category)
    if runtime_profile is not None:
        profile_path = pgsa / "runtime" / "session_runtime_profile.yaml"
        _warn_if_bad_id(issues, category, profile_path, "profile_id", runtime_profile.get("profile_id"))
        profiles = runtime_profile.get("profiles", {})
        if not isinstance(profiles, dict) or not profiles:
            issues.append(_issue(category, "warning", "runtime profile has no profiles", profile_path))
        for session, profile in profiles.items():
            if session not in session_names:
                issues.append(_issue(category, "warning", f"runtime profile references unknown session {session}", profile_path))
            if isinstance(profile, dict):
                for field in ["allowed", "denied", "requires_approval", "evidence_outputs"]:
                    if field not in profile:
                        issues.append(_issue(category, "warning", f"runtime profile {session} missing {field}", profile_path))
                allowed = profile.get("allowed", {})
                if isinstance(allowed, dict):
                    for field in ["read", "write"]:
                        for rel in _as_list(allowed.get(field)):
                            _warn_if_bad_rel_path(issues, category, profile_path, f"runtime allowed.{field}", rel)
                for rel in _as_list(profile.get("evidence_outputs")):
                    _warn_if_bad_rel_path(issues, category, profile_path, "runtime evidence_outputs", rel)

    capability = _read_optional_structured(pgsa / "runtime" / "capability_contract.yaml", issues, category)
    if capability is not None:
        capability_path = pgsa / "runtime" / "capability_contract.yaml"
        _warn_if_bad_id(issues, category, capability_path, "contract_id", capability.get("contract_id"))
        contracts = capability.get("contracts", {})
        if not isinstance(contracts, dict) or not contracts:
            issues.append(_issue(category, "warning", "capability contract has no session contracts", capability_path))
        for session, contract in contracts.items():
            if session not in session_names:
                issues.append(_issue(category, "warning", f"capability contract references unknown session {session}", capability_path))
            if not isinstance(contract, dict):
                continue
            _warn_if_bad_enum(issues, category, capability_path, f"capability contract {session} default_posture", contract.get("default_posture"), DEFAULT_POSTURES)
            for field in ["allowed_reads", "allowed_writes"]:
                for rel in _as_list(contract.get(field)):
                    _warn_if_bad_rel_path(issues, category, capability_path, f"capability contract {field}", rel)

    skills = _read_optional_structured(pgsa / "skills" / "signed_skill_manifest.yaml", issues, category)
    if skills is not None:
        skills_path = pgsa / "skills" / "signed_skill_manifest.yaml"
        _warn_if_bad_id(issues, category, skills_path, "manifest_id", skills.get("manifest_id"))
        for skill in _as_list(skills.get("skills")):
            if not isinstance(skill, dict):
                issues.append(_issue(category, "warning", "skill manifest entry should be an object", skills_path))
                continue
            for field in ["skill_id", "version", "status", "applies_to", "signed_by"]:
                if field not in skill:
                    issues.append(_issue(category, "warning", f"skill manifest entry missing {field}", skills_path))
            _warn_if_bad_id(issues, category, skills_path, "skill_id", skill.get("skill_id"))
            _warn_if_bad_enum(issues, category, skills_path, "skill risk", skill.get("risk"), RISK_LEVELS)
            _warn_if_bad_enum(issues, category, skills_path, "skill status", skill.get("status"), {"active", "draft", "deprecated", "disabled"})
            for session in _as_list(skill.get("applies_to")):
                if session not in session_names:
                    issues.append(_issue(category, "warning", f"skill applies to unknown session {session}", skills_path))
            for rel in _as_list(skill.get("depends_on")):
                _warn_if_bad_rel_path(issues, category, skills_path, "skill depends_on", rel)
        _append_duplicate_id_issues(
            issues,
            category,
            skills_path,
            "skill_id",
            [skill.get("skill_id") for skill in _as_list(skills.get("skills")) if isinstance(skill, dict)],
        )

    factory = _read_optional_structured(pgsa / "factory" / "factory_plan.yaml", issues, category)
    if factory is not None:
        factory_path = pgsa / "factory" / "factory_plan.yaml"
        _warn_if_bad_id(issues, category, factory_path, "factory_plan_id", factory.get("factory_plan_id"))
        _warn_if_bad_enum(issues, category, factory_path, "factory status", factory.get("status"), {"draft", "active", "blocked", "complete", "deprecated"})
        tasks = [task for task in _as_list(factory.get("tasks")) if isinstance(task, dict)]
        task_ids = {task.get("task_id") for task in tasks}
        _append_duplicate_id_issues(issues, category, factory_path, "factory task_id", [task.get("task_id") for task in tasks])
        if _factory_plan_has_cycle(tasks):
            issues.append(_issue(category, "warning", "factory task graph contains a dependency cycle", factory_path))
        for task in _as_list(factory.get("tasks")):
            if not isinstance(task, dict):
                issues.append(_issue(category, "warning", "factory task should be an object", factory_path))
                continue
            _warn_if_bad_id(issues, category, factory_path, "factory task_id", task.get("task_id"))
            if task.get("session") not in session_names:
                issues.append(_issue(category, "warning", f"factory task references unknown session {task.get('session')}", factory_path))
            for dep in _as_list(task.get("depends_on")):
                if dep not in task_ids:
                    issues.append(_issue(category, "warning", f"factory task dependency unknown: {dep}", factory_path))
            for rel in _as_list(task.get("outputs")):
                _warn_if_bad_rel_path(issues, category, factory_path, "factory task outputs", rel)

    for scenario in (pgsa / "scenarios").glob("*.yaml"):
        data = _read_optional_structured(scenario, issues, category)
        if data is None:
            continue
        _warn_if_bad_id(issues, category, scenario, "scenario_id", data.get("scenario_id"))
        for field in ["scenario_id", "owner_session", "contract_refs", "steps", "expected_evidence"]:
            if field not in data:
                issues.append(_issue(category, "warning", f"scenario test missing {field}", scenario))
        if data.get("owner_session") not in session_names:
            issues.append(_issue(category, "warning", f"scenario owner session unknown: {data.get('owner_session')}", scenario))
        if not _as_list(data.get("steps")):
            issues.append(_issue(category, "warning", "scenario test should include at least one step", scenario))
        if not _as_list(data.get("expected_evidence")):
            issues.append(_issue(category, "warning", "scenario test should include expected evidence", scenario))
    scenario_ids = []
    for scenario in (pgsa / "scenarios").glob("*.yaml"):
        data = _read_optional_structured(scenario, issues, category)
        if isinstance(data, dict):
            scenario_ids.append(data.get("scenario_id"))
    _append_duplicate_id_issues(issues, category, pgsa / "scenarios", "scenario_id", scenario_ids)

    event_ids = []
    for event in read_jsonl(pgsa / "evidence" / "runtime_evidence.jsonl"):
        event_ids.append(event.get("event_id"))
        for field in ["event_id", "timestamp", "session", "event_type", "status", "evidence_ref"]:
            if field not in event:
                issues.append(_issue(category, "warning", f"runtime evidence event missing {field}", pgsa / "evidence" / "runtime_evidence.jsonl"))
        evidence_path = pgsa / "evidence" / "runtime_evidence.jsonl"
        _warn_if_bad_id(issues, category, evidence_path, "runtime evidence event_id", event.get("event_id"))
        if not _looks_like_event_type(event.get("event_type")):
            issues.append(_issue(category, "warning", "runtime evidence event_type should be namespaced like runtime.file_read", evidence_path))
        _warn_if_bad_enum(issues, category, evidence_path, "runtime evidence status", event.get("status"), EVIDENCE_STATUSES)
        if "risk" in event:
            _warn_if_bad_enum(issues, category, evidence_path, "runtime evidence risk", event.get("risk"), RISK_LEVELS)
        if "resource" in event and event.get("resource") not in {"external", "none"}:
            _warn_if_bad_rel_path(issues, category, evidence_path, "runtime evidence resource", event.get("resource"))
        if event.get("session") not in session_names and event.get("session") != "system":
            issues.append(_issue(category, "warning", f"runtime evidence references unknown session {event.get('session')}", pgsa / "evidence" / "runtime_evidence.jsonl"))
    _append_duplicate_id_issues(issues, category, pgsa / "evidence" / "runtime_evidence.jsonl", "runtime evidence event_id", event_ids)

    audit_path = pgsa / "audits" / "cognitive_audit_note.md"
    if audit_path.exists():
        frontmatter = _parse_frontmatter(audit_path.read_text(encoding="utf-8"))
        if frontmatter is None:
            issues.append(_issue(category, "warning", "cognitive audit note missing YAML frontmatter", audit_path))
        else:
            for field in ["audit_id", "session", "status", "evidence_strength"]:
                if field not in frontmatter:
                    issues.append(_issue(category, "warning", f"cognitive audit note missing {field}", audit_path))
            _warn_if_bad_id(issues, category, audit_path, "cognitive audit audit_id", frontmatter.get("audit_id"))
            if frontmatter.get("session") not in session_names:
                issues.append(_issue(category, "warning", f"cognitive audit references unknown session {frontmatter.get('session')}", audit_path))
            _warn_if_bad_enum(issues, category, audit_path, "cognitive audit status", frontmatter.get("status"), {"draft", "active", "deprecated", "hypothesis_only"})
            _warn_if_bad_enum(issues, category, audit_path, "cognitive audit evidence_strength", frontmatter.get("evidence_strength"), {"hypothesis", "soft_hypothesis", "weak", "moderate", "strong"})


def issues_to_dicts(issues: list[ValidationIssue]) -> list[dict[str, str]]:
    return [issue.__dict__ for issue in issues]
