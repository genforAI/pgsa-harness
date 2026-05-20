from __future__ import annotations

from typing import Any


PROJECT_TEMPLATE: dict[str, Any] = {
    "project_id": "pgsa_project",
    "project_name": "PGSA Project",
    "goal": "Keep multi-session coding-agent work coherent across contracts, session state, reviews, integration, and handoff.",
    "modules": ["backend", "frontend", "docs", "security", "integration"],
    "acceptance": [
        "Shared contracts match producer and consumer assumptions",
        "Session summaries describe changed files, decisions, risks, and contract impact",
        "Open semantic conflicts are recorded as merge proposals",
        "integration report has no blocking drift",
    ],
}

SESSIONS_TEMPLATE: dict[str, Any] = {
    "sessions": {
        "backend": {
            "owner_scope": ["backend API", "schema", "permission logic"],
            "must_update": [
                "harness/backend.md",
                "state/backend.summary.md",
                "contracts/api.project.v1.json",
                "ledger/coherence_ledger.jsonl",
            ],
        },
        "frontend_components": {
            "owner_scope": ["frontend UI", "API consumption", "shared components"],
            "must_update": [
                "harness/frontend_components.md",
                "state/frontend_components.summary.md",
                "reviews/frontend_components_review.md",
                "ledger/coherence_ledger.jsonl",
            ],
        },
        "docs_security_integration": {
            "owner_scope": ["docs", "security checklist", "integration readiness"],
            "must_update": [
                "harness/docs_security_integration.md",
                "state/docs_security_integration.summary.md",
                "reviews/security_review.md",
                "integration/integration_report.json",
                "ledger/coherence_ledger.jsonl",
            ],
        },
    }
}

API_CONTRACT_TEMPLATE: dict[str, Any] = {
    "contract_id": "api.project.v1",
    "owner_session": "backend",
    "consumer_sessions": ["frontend_components", "docs_security_integration"],
    "status": "accepted",
    "endpoint": "GET /api/projects/:id",
    "response_shape": {
        "project_id": "string",
        "display_name": "string",
        "team_members": "array",
        "permissions": "object",
    },
    "breaking_change": False,
    "acceptance_tests": [
        "frontend consumes project_id",
        "docs describe display_name",
        "permission rule is reflected in UI",
    ],
    "last_updated_by": "backend",
    "requires_review": ["frontend_components", "docs_security_integration"],
}

SESSION_SUMMARY_TEMPLATE = """# {session} Session Summary

## Scope
{scope}

## Completed
- Initial PGSA scaffold created.

## Changed files
- none

## Decisions
- none

## Risks
- none

## Contract impact
- none

## Review requests
- none

## Integration readiness
pending
"""

SESSION_HARNESS_TEMPLATE = """# PGSA Session Harness: {session}

## Session scope
{scope}

## Required protocol

1. Read `pgsa/project.yaml` and `pgsa/sessions.yaml`.
2. Stay inside this session scope unless a contract or integration issue requires coordination.
3. Before changing shared behavior, inspect relevant contracts in `pgsa/contracts/`.
4. After local work, update this session summary in `pgsa/state/{session}.summary.md`.
5. If API, schema, component, permission, or docs assumptions changed, update the affected contract or review artifact.
6. If another session may now be inconsistent, create or update a merge proposal in `pgsa/merge_proposals/`.
7. Append a ledger event in `pgsa/ledger/coherence_ledger.jsonl`.
8. Run `pgsa validate` and `pgsa drift-report` before handoff.

## Conflict rule

Do not resolve semantic project conflict with a vague note. Use a contract update,
review gate, integration blocker, or merge proposal so the next session can see
the exact project-state issue.
"""

REVIEW_TEMPLATE = """# {name}

## Status
pending

## Blocking issues
- none

## Notes
- Initial scaffold.
"""

INTEGRATION_REPORT_TEMPLATE: dict[str, Any] = {
    "status": "pending",
    "blocking_issues": [],
    "tests_passed": None,
    "contract_violations": 0,
    "integration_failures": 0,
    "notes": "Initial scaffold.",
}
