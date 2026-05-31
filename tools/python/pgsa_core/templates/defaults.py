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
            "role": "backend-api",
            "status": "active",
            "owner_scope": ["backend API", "schema", "permission logic"],
            "produces": ["contracts/api.project.v1.json", "state/backend.summary.md"],
            "consumes": ["integration/integration_report.json"],
            "must_read": ["project.yaml", "sessions.yaml", "contracts/", "state/", "merge_proposals/"],
            "must_update": [
                "harness/backend.md",
                "state/backend.summary.md",
                "contracts/api.project.v1.json",
                "ledger/coherence_ledger.jsonl",
                "ledger/pending/",
            ],
            "handoff_to": ["frontend_components", "docs_security_integration"],
            "escalation_policy": {
                "create_merge_proposal_when": [
                    "response shape changes",
                    "permission behavior changes",
                    "consumer compatibility is unknown",
                ],
                "block_integration_when": ["required consumer review is missing"],
            },
        },
        "frontend_components": {
            "role": "frontend-ui",
            "status": "active",
            "owner_scope": ["frontend UI", "API consumption", "shared components"],
            "produces": ["state/frontend_components.summary.md", "reviews/frontend_components_review.md"],
            "consumes": ["contracts/api.project.v1.json", "integration/integration_report.json"],
            "must_read": [
                "project.yaml",
                "sessions.yaml",
                "contracts/",
                "state/backend.summary.md",
                "merge_proposals/",
            ],
            "must_update": [
                "harness/frontend_components.md",
                "state/frontend_components.summary.md",
                "reviews/frontend_components_review.md",
                "ledger/coherence_ledger.jsonl",
                "ledger/pending/",
            ],
            "handoff_to": ["docs_security_integration"],
            "escalation_policy": {
                "create_merge_proposal_when": [
                    "UI assumptions no longer match a contract",
                    "shared component behavior changes consumers",
                ],
                "block_integration_when": ["contract review is not accepted"],
            },
        },
        "docs_security_integration": {
            "role": "integration-review",
            "status": "active",
            "owner_scope": ["docs", "security checklist", "integration readiness"],
            "produces": [
                "state/docs_security_integration.summary.md",
                "reviews/security_review.md",
                "integration/integration_report.json",
                "reports/drift_report.json",
            ],
            "consumes": ["contracts/", "reviews/", "merge_proposals/", "state/"],
            "must_read": [
                "project.yaml",
                "sessions.yaml",
                "contracts/",
                "reviews/",
                "state/",
                "merge_proposals/",
                "ledger/coherence_ledger.jsonl",
            ],
            "must_update": [
                "harness/docs_security_integration.md",
                "state/docs_security_integration.summary.md",
                "reviews/security_review.md",
                "integration/integration_report.json",
                "ledger/coherence_ledger.jsonl",
            ],
            "handoff_to": [],
            "escalation_policy": {
                "create_merge_proposal_when": [
                    "contracts and consumers disagree",
                    "docs or security assumptions are stale",
                ],
                "block_integration_when": [
                    "unresolved merge proposals remain",
                    "any contract review is blocking",
                ],
            },
        },
    }
}

API_CONTRACT_TEMPLATE: dict[str, Any] = {
    "contract_id": "api.project.v1",
    "version": "1.0.0",
    "boundary_type": "api_response",
    "owner_session": "backend",
    "producer_session": "backend",
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
    "changed_fields": [],
    "acceptance_tests": [
        "frontend consumes project_id",
        "docs describe display_name",
        "permission rule is reflected in UI",
    ],
    "requires_review": ["frontend_components", "docs_security_integration"],
    "review_state": {
        "frontend_components": "accepted",
        "docs_security_integration": "accepted",
    },
    "open_merge_proposals": [],
    "last_updated_by": "backend",
    "last_updated_at": "2026-05-30T00:00:00Z",
}

SESSION_SUMMARY_TEMPLATE = """# {session} Session Summary

## Scope
{scope}

## Completed
- Initial PGSA scaffold created.

## Changed files
- none

## Produced artifacts
- none

## Consumed artifacts
- none

## Decisions
- none

## Risks
- none

## Contract impact
- none

## Review requests
- none

## Handoff targets
- none

## Integration readiness
ready
"""

SESSION_HARNESS_TEMPLATE = """# PGSA Session Harness: {session}

## Session Scope
{scope}

## Coordination Contract

This session is autonomous inside its scope. It coordinates with other sessions
only through repo-local PGSA artifacts.

## Required Protocol

1. Read `pgsa/project.yaml`.
2. Read `pgsa/sessions.yaml` and confirm this session's `role`, `produces`,
   `consumes`, `must_read`, `must_update`, and `handoff_to` fields.
3. Read relevant contracts in `pgsa/contracts/`.
4. Read open merge proposals in `pgsa/merge_proposals/`.
5. Read relevant session summaries in `pgsa/state/`.
6. Do the local task inside this session scope.
7. Update this session summary in `pgsa/state/{session}.summary.md`.
8. If shared behavior changed, update the affected contract and its
   `review_state`.
9. If a consumer may now be stale, create or update a merge proposal.
10. If integration should be blocked, update `pgsa/integration/integration_report.json`.
11. Append a ledger event in `pgsa/ledger/coherence_ledger.jsonl`. If sessions
    are running in parallel, write `pgsa/ledger/pending/{session}.event.json`
    instead and let the reviewer append accepted events to the ledger.
12. Run validation and drift reporting before handoff when available.

## Conflict Rule

Do not resolve semantic project conflict with a vague note. Use one of:

- contract update;
- review gate decision;
- integration blocker;
- merge proposal;
- ledger decision event.

The next session must be able to see the exact project-state issue without chat
history.
"""

REVIEW_TEMPLATE = """# {name}

status: accepted
blocking_issues:
  - none

## Review Scope

Initial scaffold.

## Findings

- none

## Decision

accepted
"""

INTEGRATION_REPORT_TEMPLATE: dict[str, Any] = {
    "status": "ready",
    "blocking_issues": [],
    "open_merge_proposals": [],
    "session_readiness": {
        "backend": "ready",
        "frontend_components": "ready",
        "docs_security_integration": "ready",
    },
    "contract_review_state": {"api.project.v1": "accepted"},
    "tests_passed": None,
    "contract_violations": 0,
    "integration_failures": 0,
    "notes": "Initial scaffold.",
}


ADVANCED_DIRS = [
    "gates",
    "runtime",
    "runtime/capability_requests",
    "skills",
    "evidence",
    "factory",
    "scenarios",
    "audits",
    "adapters",
]

VERIFICATION_BLUEPRINT_TEMPLATE: dict[str, Any] = {
    "blueprint_id": "project.verification.v1",
    "status": "draft",
    "notes": "Starter example. Replace command, paths, and owner_session for the target project.",
    "contract_refs": ["contracts/api.project.v1.json"],
    "required_checks": [
        {
            "check_id": "project_tests",
            "type": "project_check",
            "command": "replace-with-project-test-command",
            "owner_session": "docs_security_integration",
            "contract_refs": ["api.project.v1"],
            "evidence": "integration/integration_report.json",
        }
    ],
    "gate_policy": {
        "merge_ready_when": [
            "all required_checks pass",
            "no blocking integration issues",
            "review_router route satisfied",
        ],
        "block_when": [
            "required check fails",
            "runtime evidence contradicts contract",
            "open merge proposal remains",
        ],
    },
}

REVIEW_ROUTER_TEMPLATE: dict[str, Any] = {
    "router_id": "project.review_router.v1",
    "risk_tiers": {
        "low": "agent/session review is enough",
        "medium": "owning session plus integration review",
        "high": "human owner plus security/integration review",
        "critical": "block merge until explicit decision",
    },
    "routing_rules": [
        {
            "rule_id": "contract_breaking_change",
            "when": ["contract.breaking_change == true"],
            "route": ["owner_session", "consumer_sessions", "docs_security_integration"],
            "blocking": True,
        },
        {
            "rule_id": "runtime_denial_or_elevation",
            "when": ["runtime.capability_request.risk in high critical"],
            "route": ["docs_security_integration", "human_owner"],
            "blocking": True,
        },
    ],
}

SESSION_RUNTIME_PROFILE_TEMPLATE: dict[str, Any] = {
    "profile_id": "project.session_runtime.v1",
    "notes": "Starter example. Replace src/**, commands, and denied paths for the target project.",
    "profiles": {
        "backend": {
            "allowed": {
                "read": ["src/**", "pgsa/contracts/**", "pgsa/state/**"],
                "write": ["src/**", "pgsa/state/backend.summary.md", "pgsa/contracts/**", "pgsa/ledger/pending/**"],
                "commands": ["npm test"],
                "network": ["none"],
            },
            "requires_approval": {"read": [".env", "secrets/**"], "write": ["src/auth/**"]},
            "denied": ["~/.ssh/**", "~/.aws/**"],
            "evidence_outputs": ["pgsa/evidence/runtime_evidence.jsonl"],
        }
    },
}

CAPABILITY_CONTRACT_TEMPLATE: dict[str, Any] = {
    "contract_id": "project.capability.v1",
    "notes": "Starter example. Replace paths and session names for the target project.",
    "contracts": {
        "backend": {
            "default_posture": "least_privilege",
            "allowed_reads": ["src/**", "pgsa/contracts/**", "pgsa/state/**"],
            "allowed_writes": ["src/**", "pgsa/state/backend.summary.md", "pgsa/contracts/**", "pgsa/ledger/pending/**"],
            "requires_approval": [".env", "secrets/**", "production credentials"],
            "denied": ["~/.ssh/**", "~/.aws/**"],
        }
    },
}

SIGNED_SKILL_MANIFEST_TEMPLATE: dict[str, Any] = {
    "manifest_id": "project.skills.v1",
    "skills": [
        {
            "skill_id": "backend.contract-maintainer.v1",
            "version": "1.0.0",
            "status": "active",
            "applies_to": ["backend"],
            "signed_by": "project_owner",
            "risk": "medium",
            "depends_on": ["contracts/api.project.v1.json"],
        }
    ],
}

FACTORY_PLAN_TEMPLATE: dict[str, Any] = {
    "factory_plan_id": "project.factory.v1",
    "status": "draft",
    "notes": "Starter example. Replace tasks with the target project's real session DAG.",
    "intake": "issue_or_requirement",
    "tasks": [
        {
            "task_id": "backend_contract_update",
            "session": "backend",
            "depends_on": [],
            "outputs": ["contracts/api.project.v1.json", "state/backend.summary.md"],
            "required_evidence": ["unit_tests", "ledger_event"],
        },
        {
            "task_id": "frontend_consumer_update",
            "session": "frontend_components",
            "depends_on": ["backend_contract_update"],
            "outputs": ["state/frontend_components.summary.md", "reviews/frontend_components_review.md"],
            "required_evidence": ["consumer_review"],
        },
    ],
}

SCENARIO_TEST_TEMPLATE: dict[str, Any] = {
    "scenario_id": "project.acceptance.v1",
    "owner_session": "docs_security_integration",
    "contract_refs": ["api.project.v1"],
    "steps": [
        "Open the primary user flow",
        "Exercise the changed contract surface",
        "Capture pass/fail evidence",
    ],
    "expected_evidence": ["test command or screenshot", "review note", "integration report reference"],
}

COGNITIVE_AUDIT_NOTE_TEMPLATE = """# Cognitive Audit Note

audit_id: cogaudit_001
session: docs_security_integration
status: hypothesis_only
evidence_strength: soft_hypothesis

## Hypotheses

- No cognitive audit run. This template reserves a place for NLA/ALM-style observations.

## Evidence Boundary

Runtime evidence, tests, contracts, and review decisions are stronger evidence than this note.
"""

RUNTIME_EVIDENCE_EVENT_TEMPLATE: dict[str, Any] = {
    "event_id": "runtime_evt_001",
    "timestamp": "pending",
    "session": "system",
    "agent": "agent_id",
    "event_type": "runtime.session_started",
    "status": "observed",
    "resource": "workspace",
    "action": "start",
    "risk": "low",
    "allowed_by": "session_runtime_profile.v1",
    "contract_scope": "project",
    "evidence_ref": "local-summary",
}
