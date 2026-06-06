# PGSA Session Agent Folders

`pgsa/sessions.yaml` is the semantic registry. It defines each session's role,
scope, `must_read`, `must_update`, and handoff edges.

A session agent folder is an optional launch wrapper for a newly opened Codex,
Claude Code, SDK, or external-agent session. It gives that fresh session its own
`AGENTS.md` and `SKILL.md`, while pointing back to the shared PGSA root.

There are two valid ways to create it:

1. A user or script runs `pgsa session-agent create <session>`.
2. The session agent creates or refreshes its own folder after reading
   `pgsa/sessions.yaml`.

The second path is the protocol-native one: a fresh agent can read the registry,
confirm its session id, then create `pgsa/session_agents/<session>/AGENTS.md`,
`SKILL.md`, and `PGSA_SESSION.json` for future restarts. The generated files are
launch pointers, not a second registry.

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

Or have the active agent create the same files itself:

```text
Use PGSA session backend. Read pgsa/sessions.yaml and
pgsa-harness/protocol/session-agents/README.md. If
pgsa/session_agents/backend/ does not exist, create AGENTS.md, SKILL.md, and
PGSA_SESSION.json there. Point them back to the shared pgsa/ root, the harness
root, backend must_read/must_update artifacts, and
pgsa/skills/signed_skill_manifest.yaml.
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

The per-session `SKILL.md` is a router into that project-level accepted skill
manifest. It should not copy raw external skill instructions into the session
folder, and it should not activate anything from `pgsa/imports/sources/` by
itself.

Raw imported material under `pgsa/imports/sources/<source_id>/` is not active
guidance. A normal session should not read or apply it unless the source is in
that session's `must_read`. The `external_import_review` session is the default
exception because it is responsible for triaging and promoting imports.

This keeps external skills/harnesses reviewable and reusable by multiple
sessions without giving raw imported instructions global authority.
