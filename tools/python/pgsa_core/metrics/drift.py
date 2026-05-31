from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pgsa_core.validators.artifacts import ValidationIssue, validate


WEIGHTS = {
    "contract_violations": 2.0,
    "integration_failures": 2.0,
    "unresolved_merge_conflicts": 1.5,
    "stale_state_items": 1.2,
    "review_debt_items": 1.0,
    "repair_loops": 0.8,
}


def count_issues(issues: list[ValidationIssue]) -> dict[str, int]:
    counts = {
        "contract_violations": 0,
        "integration_failures": 0,
        "unresolved_merge_conflicts": 0,
        "stale_state_items": 0,
        "review_debt_items": 0,
        "repair_loops": 0,
        "artifact_completeness": 0,
    }
    for issue in issues:
        if issue.category in counts:
            counts[issue.category] += 1
        if issue.category == "artifact_completeness":
            counts["artifact_completeness"] += 1
    return counts


def project_drift_score(counts: dict[str, int]) -> float:
    return round(sum(WEIGHTS.get(key, 0.0) * value for key, value in counts.items()), 4)


def maintainability_score(root: Path, issues: list[ValidationIssue]) -> dict[str, Any]:
    pgsa = root / "pgsa"
    components = {
        "contract_clarity": 5,
        "session_state_clarity": 5,
        "merge_proposal_quality": 5,
        "review_traceability": 5,
        "integration_readiness": 5,
        "recovery_clarity": 5,
    }
    if any(i.category == "contract_violations" for i in issues):
        components["contract_clarity"] = 2
    if any(i.category == "stale_state_items" for i in issues):
        components["session_state_clarity"] = 3
        components["recovery_clarity"] = 3
    if any(i.category == "unresolved_merge_conflicts" for i in issues):
        components["merge_proposal_quality"] = 2
    if not list((pgsa / "reviews").glob("*.md")):
        components["review_traceability"] = 1
    if any(i.category == "integration_failures" for i in issues):
        components["integration_readiness"] = 2
    total = sum(components.values())
    return {"components": components, "total": total, "max": 30}


def drift_report(root: Path) -> dict[str, Any]:
    issues = validate(root)
    counts = count_issues(issues)
    return {
        "root": str(root),
        "issue_counts": counts,
        "project_drift_score": project_drift_score(counts),
        "maintainability_score": maintainability_score(root, issues),
        "issues": [issue.__dict__ for issue in issues],
        "recommended_next_action": recommended_next_action(counts),
    }


def recommended_next_action(counts: dict[str, int]) -> str:
    if counts.get("contract_violations"):
        return "run contract diff and update affected contracts/consumers"
    if counts.get("integration_failures"):
        return "run integration check and resolve blocking issues"
    if counts.get("unresolved_merge_conflicts"):
        return "resolve or update merge proposals"
    if counts.get("stale_state_items"):
        return "update session summaries and ledger"
    if counts.get("review_debt_items"):
        return "complete review gate"
    return "project appears coherent under current validators"


def write_drift_report(root: Path) -> Path:
    report = drift_report(root)
    path = root / "pgsa" / "reports" / "drift_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
