# AGENTS.md

This repository contains PGSA Harness Core, a repo-local project-coherence layer
for coding-agent workflows.

PGSA Harness does not live inside Codex, Claude Code, Grok Build, or any model.
It lives inside the repository. Agents read it, write to it, and use it as a
workflow layer for contracts, session summaries, semantic merge proposals,
review state, integration reports, ledger events, and drift reports.

## Agent Operating Rules

1. Read `README.md` before changing this repository.
2. Treat generated `pgsa/` artifacts as project state.
3. Treat `pgsa/harness/<session>.md` as the per-session operating surface.
4. Do not present `export-context` as the communication mechanism. It is only a
   convenience packet assembled from repo-local artifacts.
5. Treat roles as project-defined. Do not assume frontend/backend/docs/security
   are universal PGSA roles.
6. Do not present the CLI as semantic authority. It is helper automation.
7. Do not claim PGSA automatically solves every conflict. It makes project
   conflicts explicit, reviewable, and resumable.
8. Do not change claim boundaries unless explicitly asked by a maintainer.
9. Do not claim product benchmark evidence.
10. Do not claim PGSA is inside Codex, Claude Code, Grok Build, or any model.
11. When changing source code or protocol behavior, run validation and drift
   checks where relevant.
12. For external agent runs without captured commands, stdout/stderr, diffs,
   versions, timing, and evaluator metadata, label the run as `protocol run`.

## Useful Entry Points

- `commands/` contains command-style workflow prompts.
- `skills/` contains tool-specific skill bundles.
- `.agents/skills/pgsa/` contains a runtime-neutral skill.
- `hooks/` contains lifecycle hook examples that are not auto-enabled.
- `templates/` contains public-facing PGSA artifact templates.
- `rules/` contains short agent-readable boundaries.
- `roles/` contains project-defined role examples and schemas.
- `pgsa_cli/` and `core/` contain the optional Python automation.

## Architecture References

- `docs/custom-session-roles.md`
- `docs/pgsa-vs-pr-gittree.md`
- `docs/conflict-lifecycle.md`
- `docs/cli-boundary.md`
- `docs/subagents.md`

## Validation

From the repository root:

```bash
python3 -m pgsa_cli.main --help
python3 -m pgsa_cli.main --root /tmp/pgsa-smoke init --force
python3 -m pgsa_cli.main --root /tmp/pgsa-smoke validate
python3 -m pgsa_cli.main --root /tmp/pgsa-smoke drift-report
```
