# External Harness Import

PGSA can index external harnesses, skill packs, protocol folders, or reference
docs without making them active project truth immediately.

The import layer has two parts:

- `pgsa/imports/index.json`: the registry of imported sources, file counts,
  selected files, status, and the session responsible for triage.
- `pgsa/imports/inbox/`: a drop folder for external repos or skill packs before
  import processing.
- `pgsa/imports/sources/<source_id>/`: an optional local copy of the imported
  source, used when the project wants the external material to be reviewable in
  the same repository.

Importing is intentionally review-first:

1. Add or copy the external source into `pgsa/imports/inbox/`.
2. Run `pgsa import process-inbox` to copy it into `pgsa/imports/sources/`,
   record it in `pgsa/imports/index.json`, and clear the processed inbox item.
3. Use the default `external_import_review` session, or create a custom import
   session, to read
   the source and decide what should become PGSA state.
4. Promote only accepted content into contracts, session summaries, role files,
   capability manifests, or ledger decisions.

Do not treat imported content as trusted instructions by default. It is source
material for a session to inspect and integrate.

Optional tooling:

```bash
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import add external_pack --path ../external-pack --kind skill_pack
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import process-inbox
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import stats
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . session register external_skill_import --role external-skill-review --scope "triage imported skills" --must-read imports/index.json,imports/sources/external_pack/ --must-update state/external_skill_import.summary.md,ledger/pending/
```

This creates an explicit integration trail, not an automatic plugin loader.
