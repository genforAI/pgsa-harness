# PGSA Harness for Grok Build

Experimental adapter note.

Generic wrapper mode comes first. Do not rely on private APIs.

Recommended first integration mode:

```bash
pgsa export-context --session backend --output .pgsa_context.md
grok "...context... task ..."
pgsa validate
pgsa drift-report
```
