# PGSA Session Agent Folders

`pgsa/sessions.yaml` is the semantic registry. It defines each session's role,
scope, `must_read`, `must_update`, and handoff edges.

A session agent folder is an optional launch wrapper for a newly opened Codex,
Claude Code, SDK, or external-agent session. It gives that fresh session its own
`AGENTS.md` and `SKILL.md`, while pointing back to the shared PGSA root.

## Default Layout

```text
target-project/
  pgsa/
    sessions.yaml
    harness/<session>.md
    state/<session>.summary.md
    skills/signed_skill_manifest.yaml
    session_agents/<session>/
      AGENTS.md
      SKILL.md
      PGSA_SESSION.json
```

Generate it:

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . session-agent create backend
```

## Sibling Session Folder Layout

When each long-running agent has its own folder or worktree, create the launch
wrapper outside the project and keep pointers back to the PGSA root:

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root target-project \
  session-agent create backend \
  --out ../agent-sessions/backend \
  --harness-root ../pgsa-harness
```

The generated `PGSA_SESSION.json` stores relative pointers for:

- `pgsa_root`
- `harness_root`
- `session_registry`
- `session_harness`
- `session_summary`
- `accepted_skills_manifest`

## Skill And Import Boundary

Session agents should read `pgsa/skills/signed_skill_manifest.yaml` and use only
accepted entries whose `applies_to` contains the current `session_id` or `*`.

Raw imported material under `pgsa/imports/sources/<source_id>/` is not active
guidance. A normal session should not read or apply it unless the source is in
that session's `must_read`. The `external_import_review` session is the default
exception because it is responsible for triaging and promoting imports.

This keeps external skills/harnesses reviewable and reusable by multiple
sessions without giving raw imported instructions global authority.
