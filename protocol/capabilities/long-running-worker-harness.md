# Long-Running Worker Harness

The Long-Running Worker Harness adapts PGSA sessions to background coding
workers that may run across multiple turns, tools, or handoffs. Each worker
receives a repo-local session harness, declared scope, required reads, produced
artifacts, review route, and runtime profile.

PGSA does not replace dev boxes, CI, or code review. It records the project-state contract that makes those systems usable by agents.

Recommended artifacts:

- `pgsa/sessions.yaml` for ownership and handoffs
- `pgsa/runtime/session_runtime_profile.yaml` for bounded workspace permissions
- `pgsa/gates/verification_blueprint.yaml` for shift-left checks
- `pgsa/gates/review_router.yaml` for human/agent review routing
