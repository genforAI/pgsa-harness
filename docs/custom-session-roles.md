# Custom Session Roles

PGSA does not force fixed roles.

The `backend`, `frontend_components`, and `docs_security_integration` sessions
in the example project are examples only. A real project defines its own role
boundaries based on its codebase, team workflow, risk surface, and agent
capabilities.

Roles can be user-defined, agent-suggested after inspecting the project, or
adapted from another harness repository. PGSA's job is to bind those roles into
a repo-local project-coherence layer.

## Role And Session

- Role: a reusable responsibility definition, such as backend API owner,
  release integration reviewer, or data-model migration owner.
- Session: a project-specific instance of a role with concrete artifacts it
  must read and update.
- Binding: the mapping from a project session to Codex, Claude Code, generic
  agent, or other workflow surfaces.

Frontend, backend, docs, security, and integration are not required PGSA roles.
They are only a starter vocabulary.

## Example Session Binding

```yaml
sessions:
  backend_api:
    role_ref: roles/backend-api.role.yaml
    owner: user_or_agent_defined
    scope:
      - backend API
      - schema
      - auth
    external_bindings:
      codex_skill: skills/codex/SKILL.md
      claude_skill: skills/claude-code/SKILL.md
      generic_agent: .agents/skills/pgsa/SKILL.md
    must_update:
      - pgsa/contracts/
      - pgsa/state/backend_api.summary.md
      - pgsa/ledger/coherence_ledger.jsonl
```

## Agent-Suggested Roles

An agent can suggest roles after reading the project, but those roles should be
accepted, edited, or rejected by the user or maintainer. PGSA should not assume
one universal role layout.

Good role suggestions mention:

- ownership scope;
- artifacts the role must update;
- external sessions that may depend on this role;
- review or integration gates affected by the role;
- the agent surfaces that can run the role.

## External Harness Roles

A role can be imported from another harness repository if it is adapted to PGSA
artifacts. The imported role should be bound to:

- `pgsa/harness/<session>.md`;
- relevant contracts;
- session summary;
- review and integration artifacts;
- ledger events.

The role can keep its original inspiration, but PGSA's project-coherence
contract remains repo-local.

