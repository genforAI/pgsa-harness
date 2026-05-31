# Contract-to-Gate Blueprint

A PGSA contract should be more than documentation. The Contract-to-Gate pack
maps contract clauses to verification gates that a project can run with its
existing test, review, or CI tools.

Examples:

- API contract -> schema check, unit tests, consumer tests
- Component contract -> rendering or visual scenario checks
- Runtime-boundary contract -> no production code imports from `pgsa/`
- Security contract -> permission and secret-access checks

The reference artifact is `pgsa/gates/verification_blueprint.yaml`. PGSA records
the gate plan and evidence references; it does not execute or enforce those
checks unless a separate project tool consumes the artifact.
