# PGSA Harness Core

[中文说明](README.zh-CN.md)

PGSA Harness Core is an agent-first, repo-local project-coherence protocol. Version 1.1 adds optional advanced capability packs while keeping the core protocol file-based and embeddable.

It is not a Python framework and it does not live inside any model. It lives in a
repository as files that coding agents can read, update, diff, review, and carry
across sessions.

## What PGSA Does

Coding agents can finish local tasks while the project still drifts. A backend
session can change an API while a frontend session keeps the old assumption.
Docs can describe stale behavior. Local checks can pass while the project no
longer fits together.

PGSA makes that shared project state explicit:

```text
agent reads repo-local PGSA artifacts
-> agent performs the task
-> agent updates contracts, summaries, reviews, integration state, or ledger
-> next agent continues from inspectable project state
```

The communication medium is the repository, not chat history.

## Core Files

The protocol source lives under `protocol/`:

- `protocol/SKILL.md`: the agent workflow.
- `protocol/artifact-map.md`: what each PGSA artifact means.
- `protocol/templates/`: starter artifacts copied into a target repo's `pgsa/` layer.
- `protocol/schemas/`: JSON schemas for structured artifacts.
- `protocol/rules/`: short boundaries agents should follow.
- `protocol/roles/`: optional role examples and role schemas.
- `protocol/capabilities/`: optional advanced capability packs.
- `protocol/adapters/`: optional adapter specifications for runtime/security/interpretability tools.

A target project using PGSA has a `pgsa/` folder:

```text
pgsa/
  project.yaml
  sessions.yaml
  harness/
  contracts/
  state/
  merge_proposals/
  reviews/
  integration/
  ledger/
  reports/

  # optional advanced mode
  gates/
  runtime/
  skills/
  evidence/
  factory/
  scenarios/
  audits/
```

The important loop is:

1. Read `pgsa/project.yaml`.
2. Read `pgsa/sessions.yaml`.
3. Pick the active session and inspect its `role`, `produces`, `consumes`,
   `must_read`, `must_update`, and `handoff_to` fields.
4. Read `pgsa/harness/<session>.md`.
5. Read relevant contracts, summaries, reviews, integration reports, merge proposals, and ledger events.
6. Do the task.
7. Update the affected PGSA artifacts before handoff.
8. If shared assumptions changed, update a contract or create a merge proposal.

## Repository Layout

```text
protocol/   agent-facing PGSA protocol, templates, schemas, rules, and roles
examples/   small example project with a complete pgsa/ artifact layer
tools/      optional user tooling; not required by the protocol
```

Python is intentionally outside the main path. The protocol is the files.

## Embedded Use

Copy `pgsa-harness/` into any target project as a normal folder:

```text
target-project/
  pgsa-harness/
  pgsa/
  src/
  tests/
```

The agent-facing protocol is `pgsa-harness/protocol/SKILL.md`. The target
project's durable coordination state is `pgsa/`.

Optional initialization and validation can run from the embedded folder without
global installation:

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --force
# Optional advanced capability artifacts:
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --advanced --force
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . export-context --session backend
```

Agents then coordinate by reading and updating `pgsa/` artifacts. The embedded
`pgsa-harness/` folder remains the protocol and optional helper package.

## Optional Python Tools

The optional CLI can initialize and validate PGSA artifacts for users:

```bash
python3 -m pip install -e tools/python
pgsa --root examples/teamtask-projectboard validate
pgsa --root examples/teamtask-projectboard drift-report
pgsa --root /tmp/pgsa-demo init --force
```

Without installing:

```bash
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard status
```

The CLI is helper automation. It does not decide semantic truth, resolve merge
conflicts, or replace agent judgment.

For convenience, `--root` is accepted before or after the subcommand:

```bash
pgsa --root examples/teamtask-projectboard validate
pgsa validate --root examples/teamtask-projectboard
```

Advanced artifacts default to warning-level validation because they are optional
draft packs. Strict mode treats all advanced-pack warnings as blocking errors:

```bash
pgsa validate --root examples/teamtask-projectboard --strict-advanced
```

## Example

`examples/teamtask-projectboard/` contains a complete PGSA artifact layer. Start
there to see the file model without reading implementation code.

## Coordination Model

PGSA coordinates agents through repo-local artifacts:

- sessions register ownership, dependencies, and handoff targets;
- contracts define producer/consumer boundaries;
- merge proposals record semantic conflicts;
- review and integration artifacts accept or block project state;
- the ledger records decisions.

## Boundaries

PGSA does not replace PRs, worktrees, tests, code review, or integration agents.
It adds a repo-local project-state layer that makes cross-session assumptions
visible and recoverable.

PGSA Harness Core v1.1 is a local protocol release. Advanced packs are optional project-state files, not mandatory services. Current evidence is local
architecture-protocol and embedded-example evidence only. It is not a Codex,
Claude Code, Grok, OpenAI, Anthropic, or hosted-product benchmark.

## Optional Advanced Packs

Advanced packs are organized as optional layers so PGSA remains a project-state
protocol, not a replacement for CI, sandboxing, hosted orchestration, security
monitoring, or model interpretability:

- core protocol: contracts, sessions, state summaries, ledger, merge proposals,
  review gates, and integration reports;
- harness packs: verification blueprints, scenario tests, review routing, and
  factory-style planning;
- runtime adapter specs: runtime evidence, capability contracts, signed skills,
  and external runtime/security adapter records;
- research notes: cognitive audit notes and NLA/ALM-style hypotheses.

Advanced schemas intentionally describe artifact shapes and references. They do
not make PGSA enforce runtime policy by itself.

| Layer | Status | Purpose |
| --- | --- | --- |
| Core protocol | Required, stable | Project contracts, sessions, state, reviews, integration, ledger, and merge proposals. |
| Advanced packs | Optional, draft | Verification, scenario, review-routing, runtime evidence, signed skills, and factory-style planning artifacts. |
| Runtime adapters | Specs only | Interfaces for external tools that may provide runtime/security evidence. |
| Research notes | Hypothesis only | Cognitive audit notes and related observations; never stronger than tests, runtime evidence, contracts, or review decisions. |

## License

Apache License 2.0. See `LICENSE`.
