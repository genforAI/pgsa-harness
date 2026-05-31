# When To Use PGSA

Use PGSA when:

- a task changes APIs, schemas, components, permissions, docs, or test
  assumptions;
- multiple sessions or modules are involved;
- a change may leave a consumer stale;
- a project needs resumable session state;
- review or integration readiness matters.

Do not force PGSA for a tiny isolated change with no project-coherence risk.

