# PGSA Harness Command Quick Reference

PGSA Harness is harness-first and file-first. The CLI is optional helper automation for initializing, validating, and summarizing repo-local PGSA artifacts.

## Human / agent workflow surfaces

- `AGENTS.md` — root instructions for coding agents working in this repo.
- `.codex/README.md` — Codex workflow notes.
- `.agents/skills/pgsa/SKILL.md` — runtime-neutral PGSA skill.
- `skills/codex/SKILL.md` — Codex-facing skill bundle.
- `skills/claude-code/SKILL.md` — Claude Code-facing skill scaffold.
- `commands/*.md` — command-style prompts for session work.
- `hooks/*.example.sh` — lifecycle hook examples, not auto-enabled.
- `templates/` — public PGSA artifact templates.
- `rules/` — short agent-readable boundaries and workflow rules.
- `roles/` — project-defined role examples and schemas.

## Optional CLI helper commands

```bash
python3 -m pgsa_cli.main --help
python3 -m pgsa_cli.main --root examples/teamtask-projectboard status
python3 -m pgsa_cli.main --root examples/teamtask-projectboard validate
python3 -m pgsa_cli.main --root examples/teamtask-projectboard drift-report
python3 -m pgsa_cli.main --root examples/teamtask-projectboard harness --session backend
python3 -m pgsa_cli.main --root examples/teamtask-projectboard export-context --session backend
python3 -m pgsa_cli.main --root examples/teamtask-projectboard watch
python3 -m pgsa_cli.main --root examples/teamtask-projectboard queue list
```

## Boundary

The CLI is helper automation, not semantic authority. It does not decide semantic merge or final project truth.

PGSA does not make product benchmark claims. Current evidence is local generated git-worktree architecture-protocol evidence only.
