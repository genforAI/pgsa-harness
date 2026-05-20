# Generic CLI Adapter Guide

The generic CLI adapter path is protocol-first.

Use this flow when a coding assistant can read a context file or stdin:

```bash
pgsa export-context --session backend --output context.md
external-agent-command < context.md
pgsa validate
pgsa drift-report
```

The external agent is responsible for editing code and updating the relevant
`pgsa/` artifacts. PGSA does not claim product-level tool evidence unless a
separate evaluation captures real commands, prompts, transcripts, diffs, tests,
versions, timing, and a shared evaluator.
