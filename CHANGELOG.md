# Changelog

## 1.2.0 - 2026-06-05

PGSA v1.2 formalizes the practical adaptation layer around the v1.1
repo-local protocol.

### Added

- Optional Codex SDK runner documentation for repeatable multi-session PGSA
  orchestration from `pgsa/sessions.yaml`.
- Explicit SDK vs non-SDK usage guidance for Codex and Claude Code workflows.
- Review-first external skill/harness package management:
  - `pgsa/imports/inbox/` for temporary incoming packages;
  - `pgsa/imports/sources/<source_id>/` for reviewable local copies;
  - `pgsa/imports/index.json` as the import registry;
  - the default `external_import_review` session as the dedicated package-review
    role;
  - `ledger/pending/` records for accepted review events before promotion.
- Documentation that accepted import metadata can be promoted into
  `pgsa/skills/`, roles, contracts, capabilities, merge proposals, or ledger
  events, while raw unreviewed imports stay out of shipped `protocol/`.
- End-to-end external import verification against public skill sources.

### Clarified

- PGSA is still a file/protocol layer, not a plugin loader, PR merge agent,
  sandbox, CI system, or hosted orchestrator.
- `external_import_review` is a normal PGSA session with explicit `must_read`,
  `must_update`, handoff, and ledger obligations.
- Repo-local recovery snapshots should preserve scope, failed commands/checks,
  touched files, open risks, and next action.

## 1.1.0 - 2026-05-31

PGSA v1.1 introduced the public protocol/advanced-pack baseline:

- repo-local project/session/contracts/state/review/integration/ledger artifacts;
- optional advanced packs for verification, scenario tests, review routing,
  runtime evidence, signed skills, factory-style plans, and cognitive audit
  notes;
- strict advanced validation mode;
- clearer Codex/Claude Code prompt guidance for multi-session handoff.
