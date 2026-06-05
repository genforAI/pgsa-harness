# PGSA Harness Core

[ä¸­æ–‡è¯´æ˜](README.zh-CN.md)

PGSA Harness Core is an agent-first, repo-local project-coherence protocol.
Version 1.2 keeps the core protocol file-based and embeddable, while adding a
review-first package-management layer for external skills/harnesses and an
optional Codex SDK runner for repeatable multi-session orchestration.

It is not a Python framework and it does not live inside any model. It lives in
a repository as files that coding agents can read, update, diff, review, and
carry across sessions.

## What It Is

Coding agents can complete local tasks while the project still drifts. A
backend session can change an API while a frontend session keeps the old
assumption. Docs can describe stale behavior. Local checks can pass while the
project no longer fits together.

PGSA makes that shared project state explicit:

```text
agent reads repo-local PGSA artifacts
-> agent performs the task
-> agent updates contracts, summaries, reviews, integration state, or ledger drafts
-> next agent continues from inspectable project state
```

The communication medium is the repository, not private chat history.

Use PGSA when work is long-running, split across agent sessions, or likely to
change shared assumptions. For small one-off edits, it may be unnecessary.

## File Model

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
  imports/
    inbox/
    sources/
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

Core artifact roles:

| Artifact | Role |
| --- | --- |
| `project.yaml` | Project identity, goals, modules, and acceptance criteria. |
| `sessions.yaml` | Session identity, ownership, required reads, required updates, and handoff targets. |
| `harness/<session>.md` | Per-session operating instructions. |
| `contracts/*.json` | Shared producer/consumer assumptions, review state, acceptance tests, and breaking-change state. |
| `state/*.summary.md` | Compressed session memory plus recovery snapshot: scope, failed commands, touched files, open risks, and next action. |
| `merge_proposals/*.md` | Open semantic conflict records with evidence, options, and decision owner. |
| `reviews/*` | Review-gate status and blocking issues. |
| `integration/integration_report.json` | Current integration readiness, blockers, open merge proposals, and contract review state. |
| `ledger/coherence_ledger.jsonl` | Append-only accepted project-coherence events. |
| `ledger/pending/*.json` | Per-session event drafts for parallel runs, promoted by review/integration. |
| `imports/index.json` | External harness/skill/protocol import index, reviewed before activation. |
| `imports/inbox/` | Drop folder for external repos or skill packs before import processing. |
| `imports/sources/<source_id>/` | Optional copied external source material for repo-local review. |

## Built-In Packs Vs Project Import Packages

Keep bundled PGSA material separate from user-added external material:

| Location | Owner | Purpose |
| --- | --- | --- |
| `protocol/capabilities/`, `protocol/adapters/`, `protocol/templates/`, `protocol/schemas/` | PGSA harness | Shipped reference artifact shapes and optional advanced packs. |
| target project `pgsa/imports/inbox/` | user / importing agent | Temporary drop folder for external repos, skills, prompt packs, or docs. |
| target project `pgsa/imports/sources/<source_id>/` | project | Reviewable local copy of imported external material. |
| target project `pgsa/imports/index.json` | project | Import registry: source metadata, selected files, detected skills, review state, and triage session. |
| target project `pgsa/skills/` | project, advanced mode | Accepted skill provenance or signed skill manifests, not raw unreviewed imports. |

Raw external skills should not be mixed into the shipped `protocol/` folders.
They should
first enter `pgsa/imports/`, be reviewed by `external_import_review`
or a custom import-review session, and only then be promoted into project-owned
state such as `pgsa/skills/`, roles, contracts, capabilities, merge proposals,
or ledger events.

This is PGSA's package-management boundary. External skills, prompt packs,
harnesses, and reference protocols are treated as import packages: indexed,
copied, reviewed, and recorded before they can affect project state. The default
`external_import_review` session is the package-review session responsible for
triage. It is registered like any other PGSA session, with explicit
`must_read`, `must_update`, handoff, and ledger obligations.

## Core Workflow

Every agent session follows the same loop:

1. Read `pgsa/project.yaml`.
2. Read `pgsa/sessions.yaml`.
3. Identify the active session and inspect its `role`, `owner_scope`,
   `produces`, `consumes`, `must_read`, `must_update`, and `handoff_to`.
4. Read `pgsa/harness/<session>.md`.
5. Read relevant contracts, summaries, reviews, integration reports, merge
   proposals, and ledger events.
6. Do the task.
7. Update the affected PGSA artifacts before handoff.
8. If shared assumptions changed, update a contract or create a merge proposal.
9. If a decision was accepted, append a ledger event or submit a pending event
   for review.

```mermaid
flowchart LR
  A["coding-agent session"] --> B["pgsa/sessions.yaml<br/>session identity"]
  B --> C["must_read<br/>project-state inputs"]
  C --> D["task work"]
  D --> E["must_update<br/>summaries, contracts, reviews, integration"]
  E --> F["ledger/pending or accepted ledger event"]
  F --> G["next session resumes<br/>from repo-local state"]
```

## Next-Session Recovery

Repo-local state only helps if the next run can recover without replaying chat.
For that reason, each `pgsa/state/<session>.summary.md` should keep a short
recovery snapshot:

- current scope;
- last known good state;
- failed commands or checks that still matter;
- touched files, including files inspected or partially edited;
- open risks, blockers, or unresolved assumptions;
- next recommended action.

This snapshot is intentionally smaller than a transcript. It gives the next
Codex, Claude Code, or human reviewer enough context to restart work, decide
what must be re-run, and avoid repeating failed commands.

## Multi-Session Registration

PGSA is registration-based. Each project session is declared in
`pgsa/sessions.yaml` with a role, ownership scope, produced artifacts, consumed
artifacts, required reads, required updates, handoff targets, and escalation
policy.

Example session identities:

```text
backend
  owns API contracts and backend summary

frontend_components
  consumes API contracts and owns UI review state

docs_security_integration
  reads contracts, summaries, reviews, merge proposals, integration state,
  and ledger before deciding readiness

external_import_review
  triages imported harnesses, skill packs, protocols, and docs before promotion
```

The registration tells Codex, Claude Code, or another coding-agent session what
it owns, what it must inspect, and what it must update before handoff.

PGSA includes a default active `external_import_review` session for import
triage. Agents can also register a new identity when the user asks for a custom
role:

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . session register research_import \
  --role external-skill-review \
  --scope "triage imported skills and protocols" \
  --must-read imports/index.json,imports/sources/external_pack/ \
  --must-update state/research_import.summary.md,ledger/pending/ \
  --handoff-to docs_security_integration \
  --self-registered
```

This creates the `sessions.yaml` entry plus matching `harness/` and `state/`
files. The new session still has explicit scope and required artifacts; it does
not receive global authority over the repo.

## External Skill And Harness Package Management

External harnesses, skills, prompt packs, protocol folders, or docs should be
managed as reviewable packages before a session uses them.

For direct import:

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import add external_pack \
  --path ../external-pack \
  --kind skill_pack \
  --session external_import_review
```

For the inbox workflow, copy or clone external sources into
`pgsa/imports/inbox/`, then process the inbox:

```bash
cp -R ../external-pack pgsa/imports/inbox/external_pack
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import process-inbox
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import review external_pack
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import stats
```

`process-inbox` indexes each inbox item, copies it into
`pgsa/imports/sources/<source_id>/`, records it in `pgsa/imports/index.json`,
and clears the processed inbox item by default. Pass `--keep` only when you are
debugging.

`import review <source_id>` is the review step. It scans the copied source for
`SKILL.md`, README, and schema files, updates the import record to `reviewed`,
and writes the result into `harness/<session>.md`,
`state/<session>.summary.md`, and `ledger/pending/`. It still does not install
or trust the imported content automatically.

The import command records source kind, origin path, optional local copy,
selected files, file count, total bytes, detected skill entries, review
artifacts, and the recommended triage session in `pgsa/imports/index.json`.

The intended flow is review-first package management:

1. Place or copy the external source into `pgsa/imports/inbox/`.
2. Let `external_import_review` or another import-review session process it.
3. Let that session read `imports/index.json` and `imports/sources/<source_id>/`.
4. Run `pgsa import review <source_id>` or have the session write the same
   review artifacts manually.
5. Promote only accepted material into contracts, summaries, roles, capability
   manifests, `pgsa/skills/`, merge proposals, or ledger events.

Imported content is source material, not trusted project guidance. This keeps
external skills from silently changing the project contract or overriding
current PGSA state.

To run a real external import verification against public skill sources:

```bash
python3 tools/scripts/verify_external_skill_imports.py
```

The script clones external skills into a temporary project, drops them into
`pgsa/imports/inbox/`, runs `process-inbox`, runs `import review`, verifies that
the inbox was cleaned, checks review artifacts and pending ledger events, and
runs `pgsa validate`.

## Conflict Lifecycle And Ledger Boundary

PGSA does not silently auto-merge conflicting writes, and it is not a PR merge
agent. Git, PRs, CI, and code review remain the right tools for code diffs,
textual conflicts, implementation review, and final merge.

PGSA works one layer earlier: it records cross-session project semantics that
may not appear as a Git conflict.

Conflict lifecycle:

```mermaid
flowchart LR
  A["session detects semantic drift"] --> B["create/update merge_proposal"]
  B --> C["record evidence + affected contracts + options"]
  C --> D["producer / consumer / integration review"]
  D --> E["update curated state"]
  E --> F["append accepted ledger event"]
```

Boundary:

| Layer | Files | Meaning |
| --- | --- | --- |
| Current curated state | `sessions.yaml`, `contracts/`, `state/`, `merge_proposals/`, `reviews/`, `integration/` | Editable project state: roles, assumptions, open conflicts, review state, and integration readiness. |
| Pending history | `ledger/pending/*.json` | Draft event records from parallel sessions, not yet accepted. |
| Accepted history | `ledger/coherence_ledger.jsonl` | Append-only timeline of accepted project-coherence events and decisions. |

When a session detects semantic drift, such as a contract changing while a
consumer still holds the old assumption, it writes or updates
`pgsa/merge_proposals/*.md` with evidence, affected contracts, resolution
options, and a decision owner.

Only after review or integration accepts the resolution should the project append
an event to `pgsa/ledger/coherence_ledger.jsonl`. The ledger should reference
the curated artifacts; it should not become a dumping ground for raw context,
unaccepted conclusions, or full chat transcripts.

For parallel runs, sessions should write `pgsa/ledger/pending/*.json` first. The
review/integration session promotes accepted events into the coherence ledger.

## Why This Is Not PR Automation

PGSA is not a PR merge agent and does not auto-resolve Git conflicts or merge
code. PRs are still the right place to review a code diff, run CI, discuss
implementation, and merge changes.

PGSA records the project-state that coding-agent sessions need before a PR is
ready:

- which session owns which part of the project;
- which contracts and summaries must be read before editing;
- which artifacts must be updated before handoff;
- which semantic assumptions changed even when Git has no text conflict;
- why integration is ready or blocked.

The main advantage over plain PR review is semantic continuity. A backend
session can change an API in a way that still compiles, while a frontend session
keeps the old assumption. Git may not conflict and a PR may not expose the drift
until late review. PGSA records that drift as repo-local project state so the
next agent does not depend on private chat history.

## Quick Start

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
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . export-context --session backend
```

Advanced artifacts are optional:

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --advanced --force
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate --strict-advanced
```

Python is intentionally outside the main path. The protocol is the files.

## Codex And Claude Code Use

For Codex, put PGSA guidance in the target repository's `AGENTS.md`. For Claude
Code, put the equivalent guidance in `CLAUDE.md`; this repository includes both
files as examples.

Minimal Codex prompt:

```text
Use PGSA session backend. Read AGENTS.md, pgsa-harness/protocol/SKILL.md,
pgsa/sessions.yaml, and the backend must_read artifacts before editing. Work
inside the backend owner_scope unless a merge proposal is needed. Update backend
must_update artifacts before handoff.
```

Minimal Claude Code prompt:

```text
Use PGSA session frontend_components. Read CLAUDE.md,
pgsa-harness/protocol/SKILL.md, pgsa/sessions.yaml, and the frontend_components
must_read artifacts before editing. If UI assumptions no longer match a
contract, create or update a merge proposal instead of relying on conversation
memory.
```

Multiple sessions can run from separate terminals, separate worktrees, or
separate agent threads. Give each one a distinct PGSA ¥‘•¹Ñ¥Ñäè()‰…Í )½‘•à€‰UÍ”AMÍ•ÍÍ¥½¸‰…­•¹¸I•…9QL¹µ°ÁÍ„µ¡…É¹•ÍÌ½ÁÉ½Ñ½½°½M-%10¹µ°ÁÍ„½Í•ÍÍ¥½¹Ì¹å…µ°°…¹Ñ¡”‰…­•¹µÕÍÑ}É•……ÉÑ¥™…ÑÌ¸UÁ‘…Ñ”‰…­•¹µÕÍÑ}ÕÁ‘…Ñ”…ÉÑ¥™…ÑÌ‰•™½É”¡…¹‘½™˜¸ˆ()½‘•à€‰UÍ”AMÍ•ÍÍ¥½¸™É½¹Ñ•¹‘}½µÁ½¹•¹ÑÌ¸I•…9QL¹µ°ÁÍ„µ¡…É¹•ÍÌ½ÁÉ½Ñ½½°½M-%10¹µ°ÁÍ„½Í•ÍÍ¥½¹Ì¹å…µ°°™É½¹Ñ•¹‘}½µÁ½¹•¹ÑÌµÕÍÑ}É•……ÉÑ¥™…ÑÌ°…¹‰…­•¹½¹ÑÉ…ĞÍÑ…Ñ”¸UÁ‘…Ñ”™É½¹Ñ•¹µÕÍÑ}ÕÁ‘…Ñ”…ÉÑ¥™…ÑÌ‰•™½É”¡…¹‘½™˜¸ˆ()½‘•à€‰UÍ”AMÍ•ÍÍ¥½¸‘½Í}Í•ÕÉ¥Ñå}¥¹Ñ•É…Ñ¥½¸¸I•…9QL¹µ°ÁÍ„µ¡…É¹•ÍÌ½ÁÉ½Ñ½½°½M-%10¹µ°…±°ÍÕµµ…É¥•Ì°É•Ù¥•İÌ°½¹ÑÉ…ÑÌ°µ•É”ÁÉ½Á½Í…±Ì°¥¹Ñ•É…Ñ¥½¸ÍÑ…Ñ”°…¹±•‘•È¸•¥‘”É•…‘¥¹•ÍÌ…¹‰±½¬¥¹Ñ•É…Ñ¥½¸¥˜Õ¹É•Í½±Ù•Í•µ…¹Ñ¥Œ‘É¥™ĞÉ•µ…¥¹Ì¸ˆ)€()±…Õ‘”½‘”…¸‰”±…Õ¹¡•Ñ¡”Í…µ”İ…äİ¥Ñ ±…Õ‘”€‰UÍ”AMÍ•ÍÍ¥½¸€¸¸¸‰€¸()½È½‘•àÍÕ‰…•¹Ğİ½É­™±½İÌ°­••ÀÑ¡”Á…É•¹ĞÍ•ÍÍ¥½¸…ÌÑ¡”¥¹Ñ•É…Ñ½È…¹…Í¬)ÍÕ‰…•¹ÑÌÑ¼É•ÑÕÉ¸AMµÉ•…‘äÍÕµµ…É¥•Ì¥¹ÍÑ•…½˜İÉ¥Ñ¥¹œ•Ù•Éä…ÉÑ¥™…Ğ)‘¥É•Ñ±ä¸((ŒŒ=ÁÑ¥½¹…°½‘•àM,•µ¼()Q¡”½ÁÑ¥½¹…°Í‘¬½€™½±‘•È¥Ì™½ÈÕÍ•ÉÌİ¡¼…±É•…‘äİ…¹ĞÑ¼ÉÕ¸AMÍ•ÍÍ¥½¹Ì)Ñ¡É½Õ Ñ¡”½‘•àM,¸%Ğ¥Ì„ÕÍ•É±…¹‘•µ¼°¹½ĞÑ¡”½É”AMÁ…Ñ …¹¹½Ğ…¸)=Á•¹$•¹‘½ÉÍ•µ•¹Ğ½È¥¹Ñ•É…Ñ¥½¸±…¥´¸Q¡”M,É•™•É•¹”¥Ì(ñ¡ÑÑÁÌè¼½‘•Ù•±½Á•ÉÌ¹½Á•¹…¤¹½´½½‘•à½Í‘¬ÁåÑ¡½¸µ±¥‰É…Éäø¸()AMÍÕÁÁ½ÉÑÌÑİ¼½‘•àÕÍ…”µ½‘•Ìè()ğ5½‘”ğ!½Ü¥Ğİ½É­Ìğ	•ÍĞ™½ÈğQÉ…‘•½™˜ğ)ğ€´´´ğ€´´´ğ€´´´ğ€´´´ğ)ğ]¥Ñ¡½ÕĞM,ğMÑ…ÉĞ½‘•àµ…¹Õ…±±ä…¹¥Ù”¥Ğ„AMÍ•ÍÍ¥½¸ÁÉ½µÁĞ°™½È•á…µÁ±”UÍ”AMÍ•ÍÍ¥½¸‰…­•¹¸¸¹€¸½‘•àÉ•…‘Ì9QL¹µ‘€°ÁÉ½Ñ½½°½M-%10¹µ‘€°…¹ÁÍ„½€…ÉÑ¥™…ÑÌ‘¥É•Ñ±ä¸ğ9½Éµ…°¥¹Ñ•É…Ñ¥Ù”İ½É¬°½¹”µ½™˜Í•ÍÍ¥½¹Ì°µ…¹Õ…°½¹ÑÉ½°°…¹µ…á¥µÕ´ÑÉ…¹ÍÁ…É•¹ä¸ğQ¡”ÕÍ•ÈÍÑ…ÉÑÌ…¹½½É‘¥¹…Ñ•Ì•… Í•ÍÍ¥½¸µ…¹Õ…±±ä¸ğ)ğ]¥Ñ M,ğÍ‘¬½½‘•á}ÁÍ…}ÉÕ¹¹•È¹Áå€É•…‘ÌÁÍ„½Í•ÍÍ¥½¹Ì¹å…µ±€°‰Õ¥±‘Ì½¹”AMµ…İ…É”ÁÉ½µÁĞÁ•ÈÍ•ÍÍ¥½¸°ÍÑ…ÉÑÌ½‘•àM,Ñ¡É•…‘Ì¥¸Ñ¡”Ñ…É•Ğ€´µÉ½½Ñ€°…¹…Í­Ì•… Ñ¡É•…Ñ¼ÕÁ‘…Ñ”µÕÍÑ}ÕÁ‘…Ñ•€…ÉÑ¥™…ÑÌ¸ğAÉ½É…µµ…Ñ¥Œ½É¡•ÍÑÉ…Ñ¥½¸°É•Á•…Ñ•±½¹œµÉÕ¹¹¥¹œ¡•­Ì°$½¥¹Ñ•É¹…°Ñ½½±Ì°…¹±…Õ¹¡¥¹œµÕ±Ñ¥Á±”É•¥ÍÑ•É•Í•ÍÍ¥½¹Ì½¹Í¥ÍÑ•¹Ñ±ä¸ğI•ÅÕ¥É•ÌÑ¡”½ÁÑ¥½¹…°½‘•àM,…¹É•µ…¥¹ÌÕÍ•É±…¹½É¡•ÍÑÉ…Ñ¥½¸ìAMÍÑ¥±°‘½•Ì¹½Ğ‰åÁ…ÍÌ½‘•àÍ…¹‘‰½á¥¹œ½È…ÁÁÉ½Ù…±Ì¸ğ()Q¡”M,…‘Ù…¹Ñ…”¥ÌÉ•Á•…Ñ…‰¥±¥Ñä¸%ĞÑÕÉ¹ÌÑ¡”Í…µ”É•Á¼µ±½…°AMÍ•ÍÍ¥½¸)É•¥ÍÑÉä¥¹Ñ¼½¹Í¥ÍÑ•¹Ğ½‘•àÑ¡É•…ÍÑ…ÉÑÌ°İ¡¥±”Ñ¡”¹½¸µM,Á…Ñ É•µ…¥¹ÌÑ¡”)Á±…¥¸™¥±”½ÁÉ½Ñ½½°İ½É­™±½Ü™½È•Ù•Éå‘…ä¥¹Ñ•É…Ñ¥Ù”ÕÍ”¸()‰…Í )ÁåÑ¡½¸ÌÍ‘¬½½‘•á}ÁÍ…}ÉÕ¹¹•È¹Áä€´µÉ½½Ğ€¸€´µ½¹™¥œÍ‘¬½½‘•àµÉÕ¹¹•È¹½¹™¥œ¹•á…µÁ±”¹©Í½¸€´µ‘ÉäµÉÕ¸)€()½È„É•…°M,ÉÕ¸°¥¹ÍÑ…±°Ñ¡”½™™¥¥…°M,Í•Á…É…Ñ•±äè()‰…Í )Á¥À¥¹ÍÑ…±°½Á•¹…¤µ½‘•à)ÁåÑ¡½¸ÌÍ‘¬½½‘•á}ÁÍ…}ÉÕ¹¹•È¹Áä€´µÍÑ…ÉĞµ½¹±ä)ÁåÑ¡½¸ÌÍ‘¬½½‘•á}ÁÍ…}ÉÕ¹¹•È¹Áä€´µÉ½½Ğ€¸€´µ½¹™¥œÍ‘¬½½‘•àµÉÕ¹¹•È¹½¹™¥œ¹•á…µÁ±”¹©Í½¸)€()Q¡”ÉÕ¹¹•ÈÉ•…‘ÌÁÍ„½Í•ÍÍ¥½¹Ì¹å…µ±€°‰Õ¥±‘Ì½¹”AMµ…İ…É”ÁÉ½µÁĞÁ•È)É•¥ÍÑ•É•Í•ÍÍ¥½¸°ÍÑ…ÉÑÌ•… ½‘•àM,Ñ¡É•…¥¸Ñ¡”Ñ…É•ĞÁÉ½©•ĞÉ½½Ğ)Á…ÍÍ•‰ä€´µÉ½½Ñ€°…¹…Í­Ì•… Ñ¡É•…Ñ¼ÕÁ‘…Ñ”¥ÑÌµÕÍÑ}ÕÁ‘…Ñ•€…ÉÑ¥™…ÑÌ)‰•™½É”¡…¹‘½™˜¸%ĞÍÑ…åÌÕÍ•É±…¹½É¡•ÍÑÉ…Ñ¥½¸èAMÉ•µ…¥¹ÌÑ¡”™¥±”ÁÉ½Ñ½½°°)…¹½‘•àÍ…¹‘‰½á¥¹œ½…ÁÁÉ½Ù…±ÌÉ•µ…¥¸½‘•àÌÉ•ÍÁ½¹Í¥‰¥±¥Ñä¸½ÈÑ•µÁ½É…Éä)Ù•É¥™¥…Ñ¥½¸ÉÕ¹Ì°Í•Ğ€‰•Á¡•µ•É…°ˆèÑÉÕ•€¥¸Ñ¡”M,½¹™¥œì±•…Ù”¥Ğ™…±Í•€)İ¡•¸M,µÉÕ¸Í•ÍÍ¥½¹ÌÍ¡½Õ±¥É•µ…¥¸É•ÍÕµ…‰±”¸((ŒŒ=ÁÑ¥½¹…°AåÑ¡½¸Q½½±Ì()Q¡”½ÁÑ¥½¹…°1$…¸¥¹¥Ñ¥…±¥é”…¹Ù…±¥‘…Ñ”AM…ÉÑ¥™…ÑÌ™½ÈÕÍ•ÉÌè()‰…Í )ÁåÑ¡½¸Ì€µ´Á¥À¥¹ÍÑ…±°€€µ”Ñ½½±Ì½ÁåÑ¡½¸)ÁÍ„€´µÉ½½Ğ•á…µÁ±•Ì½Ñ•…µÑ…Í¬µÁÉ½©•Ñ‰½…ÉÙ…±¥‘…Ñ”)ÁÍ„€´µÉ½½Ğ•á…µÁ±•Ì½Ñ•…µÑ…Í¬µÁÉ½©•Ñ‰½…É‘É¥™ĞµÉ•Á½ÉĞ)ÁÍ„€´µÉ½½Ğ€½ÑµÀ½ÁÍ„µ‘•µ¼¥¹¥Ğ€´µ™½É”)€()]¥Ñ¡½ÕĞ¥¹ÍÑ…±±¥¹œè()‰…Í )AeQ!=9AQ õÑ½½±Ì½ÁåÑ¡½¸ÁåÑ¡½¸Ì€µ´ÁÍ…}±¤¹µ…¥¸€´µÉ½½Ğ•á…µÁ±•Ì½Ñ•…µÑ…Í¬µÁÉ½©•Ñ‰½…ÉÍÑ…ÑÕÌ)€()½È½¹Ù•¹¥•¹”°€´µÉ½½Ñ€¥Ì…•ÁÑ•‰•™½É”½È…™Ñ•ÈÑ¡”ÍÕ‰½µµ…¹è()‰…Í )ÁÍ„€´µÉ½½Ğ•á…µÁ±•Ì½Ñ•…µÑ…Í¬µÁÉ½©•Ñ‰½…ÉÙ…±¥‘…Ñ”)ÁÍ„Ù…±¥‘…Ñ”€´µÉ½½Ğ•á…µÁ±•Ì½Ñ•…µÑ…Í¬µÁÉ½©•Ñ‰½…É)€()Q¡”1$¥Ì¡•±Á•È…ÕÑ½µ…Ñ¥½¸¸%Ğ‘½•Ì¹½Ğ‘•¥‘”Í•µ…¹Ñ¥ŒÑÉÕÑ °É•Í½±Ù”µ•É”)½¹™±¥ÑÌ°½ÈÉ•Á±…”…•¹Ğ©Õ‘µ•¹Ğ¸((ŒŒ]¡…ĞØÄ¸È‘‘Ì()Y•ÉÍ¥½¸€Ä¸È‰Õ¥±‘Ì½¸Ñ¡”ØÄ¸ÄÁÉ½Ñ½½°½…‘Ù…¹•µÁ…¬‰…Í•±¥¹”‰ä™½Éµ…±¥é¥¹œ)Ñİ¼ÁÉ…Ñ¥…°ÕÍ…”±…å•ÉÌè½ÁÑ¥½¹…°½‘•àM,½É¡•ÍÑÉ…Ñ¥½¸…¹É•Ù¥•Üµ™¥ÉÍĞ)•áÑ•É¹…°Í­¥±°½¡…É¹•ÍÌÁ…­…”µ…¹…•µ•¹Ğ¸()½µÁ…É•İ¥Ñ Ñ¡”ØÄ¸Ä‰…Í•±¥¹”è()ğ€Ä¸Ä‰…Í•±¥¹”ğ€Ä¸È¥µÁÉ½Ù•µ•¹Ğğ)ğ€´´´ğ€´´´ğ)ğ½É”ÁÉ½Ñ½½°Á±ÕÌ½ÁÑ¥½¹…°…‘Ù…¹•Á…­Ì¸ğáÑ•É¹…°Í­¥±°½¡…É¹•ÍÌÁ…­…”µ…¹…•µ•¹ĞÑ¡É½Õ ¥µÁ½ÉÑÌ½¥¹‰½à½€°¥µÁ½ÉÑÌ½Í½ÕÉ•Ì½€°¥µÁ½ÉÑÌ½¥¹‘•à¹©Í½¹€°…¹Ñ¡”‘•‘¥…Ñ••áÑ•É¹…±}¥µÁ½ÉÑ}É•Ù¥•İ€Í•ÍÍ¥½¸¸ğ)ğ•¹ÑÌ½Õ±É•…AM™¥±•Ìµ…¹Õ…±±ä¸ğ½¹É•Ñ”¹½¸µM,ÁÉ½µÁÑÌÁ±ÕÌ…¸½ÁÑ¥½¹…°½‘•àM,ÉÕ¹¹•ÈÑ¡…ĞÍÑ…ÉÑÌÉ•¥ÍÑ•É•AMÍ•ÍÍ¥½¹ÌÉ•Á•…Ñ…‰±ä™É½´ÁÍ„½Í•ÍÍ¥½¹Ì¹å…µ±€¸ğ)ğ%µÁ½ÉÑ•µ…Ñ•É¥…°½Õ±‰”É•™•É•¹•‰ä½¹Ù•¹Ñ¥½¸¸ğ%µÁ½ÉÑ•Á…­…•Ì…É”½Á¥•°¥¹‘•á•°É•Ù¥•İ•°ÍÕµµ…É¥é•°…¹É•½É‘•¥¸Á•¹‘¥¹œ±•‘•È•Ù•¹ÑÌ‰•™½É”ÁÉ½µ½Ñ¥½¸¸ğ)ğM­¥±°ÁÉ½Ù•¹…¹”•á¥ÍÑ•…Ì…¸…‘Ù…¹•…ÉÑ¥™…ĞÍ¡…Á”¸ğ•ÁÑ•¥µÁ½ÉĞµ•Ñ…‘…Ñ„…¸‰”ÁÉ½µ½Ñ•¥¹Ñ¼ÁÍ„½Í­¥±±Ì½€ìÉ…ÜÕ¹É•Ù¥•İ••áÑ•É¹…°½¹Ñ•¹ĞÍÑ…åÌ½ÕĞ½˜Í¡¥ÁÁ•ÁÉ½Ñ½½°½€¸ğ)ğI•½Ù•Éä…¹½¹™±¥Ğ…ÉÑ¥™…ÑÌ•á¥ÍÑ•¸ğI5¹½Ü‘½Õµ•¹ÑÌÑ¡”‘…¥±äµÕÍ”Á…Ñ èÉ•½Ù•ÉäÍ¹…ÁÍ¡½ÑÌ°µÕÍÑ}É•…‘€½µÕÍÑ}ÕÁ‘…Ñ•€°Í•µ…¹Ñ¥Œ½¹™±¥ÑÌ°±•‘•È‰½Õ¹‘…É¥•Ì°M,ÙÌ¹½¸µM,ÕÍ”°…¹¥µÁ½ÉĞµÁ…­…”É•Ù¥•Ü¸ğ()Q¡”ØÄ¸ÈÁ…­…”µµ…¹…•µ•¹ĞÁ…Ñ ¥Ì¥¹Ñ•¹Ñ¥½¹…±±ä¹…ÉÉ½Üè()Ñ•áĞ)•áÑ•É¹…°Í½ÕÉ”(´øÁÍ„½¥µÁ½ÉÑÌ½¥¹‰½à¼(´øÁÍ„¥µÁ½ÉĞÁÉ½•ÍÌµ¥¹‰½à(´øÁÍ„½¥µÁ½ÉÑÌ½Í½ÕÉ•Ì¼ñÍ½ÕÉ•}¥ø¼€¬¥µÁ½ÉÑÌ½¥¹‘•à¹©Í½¸(´ø•áÑ•É¹…±}¥µÁ½ÉÑ}É•Ù¥•ÜÍ•ÍÍ¥½¸(´øÉ•Ù¥•Ü…ÉÑ¥™…ÑÌ€¬±•‘•È½Á•¹‘¥¹œ¼(´ø…•ÁÑ•ÁÉ½µ½Ñ¥½¸¥¹Ñ¼ÁÍ„½Í­¥±±Ì°½¹ÑÉ…ÑÌ°É½±•Ì°…Á…‰¥±¥Ñ¥•Ì°½È±•‘•È)€()Q¡”Õ¹‘•É±å¥¹œØÄ¸Ä…‘Ù…¹•…É•…ÌÉ•µ…¥¸è()ğÉ•„ğ¥±•Ìğ]¡…Ğ¥Ğ…‘‘Ìğ)ğ€´´´ğ€´´´ğ€´´´ğ)ğM•ÍÍ¥½¸É•¥ÍÑÉäğÁÍ„½Í•ÍÍ¥½¹Ì¹å…µ±€ğ±•…ÈÍ•ÍÍ¥½¸¥‘•¹Ñ¥Ñä°½İ¹•ÉÍ¡¥À°µÕÍÑ}É•…‘€°µÕÍÑ}ÕÁ‘…Ñ•€°¡…¹‘½™˜°…¹•Í…±…Ñ¥½¸ÉÕ±•Ì¸ğ)ğM•µ…¹Ñ¥Œ½¹™±¥ÑÌğÁÍ„½µ•É•}ÁÉ½Á½Í…±Ì½€ğI•Ù¥•İ…‰±”É•½É‘Ì™½È…ÍÍÕµÁÑ¥½¸‘É¥™ĞÑ¡…Ğµ…ä¹½Ğ…ÁÁ•…È…Ì„¥Ğ½¹™±¥Ğ¸ğ)ğY•É¥™¥…Ñ¥½¸Á±…¹¹¥¹œğÁÍ„½…Ñ•Ì½€°ÁÍ„½Í•¹…É¥½Ì½€ğY•É¥™¥…Ñ¥½¸‰±Õ•ÁÉ¥¹ÑÌ…¹Í•¹…É¥¼Ñ•ÍÑÌÑ¡…Ğ‘•ÍÉ¥‰”İ¡…Ğ•Ù¥‘•¹”Í¡½Õ±•á¥ÍĞ‰•™½É”¥¹Ñ•É…Ñ¥½¸¸ğ)ğI•Ù¥•ÜÉ½ÕÑ¥¹œğÁÍ„½É•Ù¥•İÌ½€ğI¥Í¬µ…İ…É”É•Ù¥•ÜµÉ½ÕÑ¥¹œ…ÉÑ¥™…ÑÌ™½È‘•¥‘¥¹œİ¡¼½Èİ¡…ĞÍ¡½Õ±¥¹ÍÁ•Ğ„¡…¹”¸ğ)ğIÕ¹Ñ¥µ”•Ù¥‘•¹”ğÁÍ„½ÉÕ¹Ñ¥µ”½€°ÁÍ„½•Ù¥‘•¹”½€ğI•½É‘Ì™É½´•áÑ•É¹…°ÉÕ¹Ñ¥µ”½Í•ÕÉ¥ÑäÑ½½±Ìİ¥Ñ¡½ÕĞ±…¥µ¥¹œAM•¹™½É•ÌÉÕ¹Ñ¥µ”Á½±¥ä¥ÑÍ•±˜¸ğ)ğ…Á…‰¥±¥Ñä½¹ÑÉ…ÑÌğÁÍ„½ÉÕ¹Ñ¥µ”½€ğáÁ±¥¥Ğ…Á…‰¥±¥Ñä…¹…ÁÁÉ½Ù…°•áÁ•Ñ…Ñ¥½¹Ì™½ÈÍ•ÍÍ¥½¹Ì½ÈÑ½½±Ì¸ğ)ğM¥¹•Í­¥±±ÌğÁÍ„½Í­¥±±Ì½€ğ=ÁÑ¥½¹…°Í­¥±°ÁÉ½Ù•¹…¹”É•½É‘Ì°‘¥•ÍÑÌ°…¹ÑÉÕÍĞµ•Ñ…‘…Ñ„¸ğ)ğ…Ñ½ÉäµÍÑå±”Á±…¹¹¥¹œğÁÍ„½™…Ñ½Éä½€ğQ…Í¬Ì…¹‘•½µÁ½Í¥Ñ¥½¸Á±…¹Ìì¹½Ğ…¸…ÕÑ½¹½µ½ÕÌ™…Ñ½Éä½È¡½ÍÑ•½É¡•ÍÑÉ…Ñ½È¸ğ)ğ½¹¥Ñ¥Ù”…Õ‘¥Ğ¹½Ñ•ÌğÁÍ„½…Õ‘¥ÑÌ½€ğ!åÁ½Ñ¡•Í¥Ìµ½¹±äÉ•Í•…É ¹½Ñ•Ìì¹½Ğµ½‘•°¥¹Ñ•ÉÁÉ•Ñ…‰¥±¥Ñä•Ù¥‘•¹”‰ä¥ÑÍ•±˜¸ğ()±°…‘Ù…¹•Á…­Ì…É”½ÁÑ¥½¹…°¸Q¡•ä…É”É•Á¼µ±½…°…ÉÑ¥™…ĞÍ¡…Á•Ì°¹½Ğ)Í•ÉÙ¥•Ì°‘…•µ½¹Ì°$°Í…¹‘‰½á¥¹œ°µ•É”…ÕÑ½µ…Ñ¥½¸°½ÈÍ•ÕÉ¥Ñä•¹™½É•µ•¹Ğ¸((ŒŒ1…å•ÉÌ()‘Ù…¹•Á…­Ì…É”½É…¹¥é•…Ì½ÁÑ¥½¹…°±…å•ÉÌÍ¼AMÉ•µ…¥¹Ì„ÁÉ½©•ĞµÍÑ…Ñ”)ÁÉ½Ñ½½°è()ğ1…å•ÈğMÑ…ÑÕÌğAÕÉÁ½Í”ğ)ğ€´´´ğ€´´´ğ€´´´ğ)ğ½É”ÁÉ½Ñ½½°ğI•ÅÕ¥É•°ÍÑ…‰±”ğAÉ½©•Ğ½¹ÑÉ…ÑÌ°Í•ÍÍ¥½¹Ì°ÍÑ…Ñ”°É•Ù¥•İÌ°¥¹Ñ•É…Ñ¥½¸°±•‘•È°…¹µ•É”ÁÉ½Á½Í…±Ì¸ğ)ğ‘Ù…¹•Á…­Ìğ=ÁÑ¥½¹…°°‘É…™ĞğY•É¥™¥…Ñ¥½¸°Í•¹…É¥¼°É•Ù¥•ÜµÉ½ÕÑ¥¹œ°ÉÕ¹Ñ¥µ”•Ù¥‘•¹”°Í¥¹•Í­¥±±Ì°…¹™…Ñ½ÉäµÍÑå±”Á±…¹¹¥¹œ…ÉÑ¥™…ÑÌ¸ğ)ğIÕ¹Ñ¥µ”…‘…ÁÑ•ÉÌğMÁ•Ì½¹±äğ%¹Ñ•É™…•Ì™½È•áÑ•É¹…°Ñ½½±ÌÑ¡…Ğµ…äÁÉ½Ù¥‘”ÉÕ¹Ñ¥µ”½Í•ÕÉ¥Ñä•Ù¥‘•¹”¸ğ)ğI•Í•…É ¹½Ñ•Ìğ!åÁ½Ñ¡•Í¥Ì½¹±äğ½¹¥Ñ¥Ù”…Õ‘¥Ğ¹½Ñ•Ì…¹É•±…Ñ•½‰Í•ÉÙ…Ñ¥½¹Ìì¹•Ù•ÈÍÑÉ½¹•ÈÑ¡…¸Ñ•ÍÑÌ°ÉÕ¹Ñ¥µ”•Ù¥‘•¹”°½¹ÑÉ…ÑÌ°½ÈÉ•Ù¥•Ü‘•¥Í¥½¹Ì¸ğ()‘Ù…¹•Í¡•µ…Ì¥¹Ñ•¹Ñ¥½¹…±±ä‘•ÍÉ¥‰”…ÉÑ¥™…ĞÍ¡…Á•Ì…¹É•™•É•¹•Ì¸Q¡•ä‘¼)¹½Ğµ…­”AM•¹™½É”ÉÕ¹Ñ¥µ”Á½±¥ä‰ä¥ÑÍ•±˜¸((ŒŒá…µÁ±”()•á…µÁ±•Ì½Ñ•…µÑ…Í¬µÁÉ½©•Ñ‰½…É½€½¹Ñ…¥¹Ì„½µÁ±•Ñ”AM…ÉÑ¥™…Ğ±…å•È¸MÑ…ÉĞ)Ñ¡•É”Ñ¼Í•”Ñ¡”™¥±”µ½‘•°İ¥Ñ¡½ÕĞÉ•…‘¥¹œ¥µÁ±•µ•¹Ñ…Ñ¥½¸½‘”¸((ŒŒ	½Õ¹‘…É¥•Ì()AM‘½•Ì¹½ĞÉ•Á±…”AIÌ°İ½É­ÑÉ••Ì°Ñ•ÍÑÌ°½‘”É•Ù¥•Ü°$°Í•ÕÉ¥ÑäÑ½½±¥¹œ°)Í…¹‘‰½á¥¹œ°½È¥¹Ñ•É…Ñ¥½¸…•¹ÑÌ°…¹¥Ğ¥Ì¹½Ğ„AHµ•É”…•¹Ğ¸%Ğ…‘‘Ì„)É•Á¼µ±½…°ÁÉ½©•ĞµÍÑ…Ñ”±…å•ÈÑ¡…Ğµ…­•ÌÉ½ÍÌµÍ•ÍÍ¥½¸…ÍÍÕµÁÑ¥½¹ÌÙ¥Í¥‰±”…¹)É•½Ù•É…‰±”¸()AM!…É¹•ÍÌ½É”ØÄ¸È¥Ì„±½…°ÁÉ½Ñ½½°É•±•…Í”¸‘Ù…¹•Á…­Ì…¹¥µÁ½ÉĞ)Á…­…”µ…¹…•µ•¹Ğ…É”½ÁÑ¥½¹…°ÁÉ½©•ĞµÍÑ…Ñ”™¥±•Ì…¹İ½É­™±½İÌ°¹½Ğµ…¹‘…Ñ½ÉäÍ•ÉÙ¥•Ì¸ÕÉÉ•¹Ğ•Ù¥‘•¹”¥Ì±½…°)…É¡¥Ñ•ÑÕÉ”µÁÉ½Ñ½½°…¹•µ‰•‘‘•µ•á…µÁ±”•Ù¥‘•¹”½¹±ä¸%Ğ¥Ì¹½Ğ„½‘•à°)±…Õ‘”½‘”°É½¬°=Á•¹$°¹Ñ¡É½Á¥Œ°½È¡½ÍÑ•µÁÉ½‘ÕĞ‰•¹¡µ…É¬¸((ŒŒ1¥•¹Í”()Á…¡”1¥•¹Í”€È¸À¸M•”1%9M€¸(