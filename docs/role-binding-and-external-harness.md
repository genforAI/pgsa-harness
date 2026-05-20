# Role Binding And External Harnesses

PGSA can use role ideas from other harness repositories, but it does not import
their product identity or assumptions.

The binding step turns a role into a PGSA session:

1. Define the role responsibility.
2. Assign a project-specific session name.
3. Bind the session to agent surfaces such as Codex, Claude Code, or generic
   CLI.
4. Bind the session to required PGSA artifacts.
5. Record cross-session dependencies.

## Binding Record

A session binding should answer:

- What project scope does this session own?
- Which contracts can this session change?
- Which other sessions consume its decisions?
- Which review or integration gates must be updated?
- Which agent-facing skill, command, or hook should be used?

## Boundary

External harness content can provide role vocabulary, command style, or hook
ideas. PGSA still requires repo-local artifacts for project state:

- contracts;
- summaries;
- merge proposals;
- reviews;
- integration reports;
- ledger events.

If an external role changes shared project behavior, the PGSA contract and
ledger must still be updated.

