# External Skill And Harness Package Management

PGSA can index external harnesses, skill packs, protocol folders, or reference
docs without making them active project truth immediately. In v1.2 this layer is
the review-first package-management path for user-added skills and harnesses.

The import layer has four parts:

- `pgsa/imports/index.json`: the registry of imported sources, file counts,
  selected files, status, and the session responsible for triage.
- `pgsa/imports/inbox/`: a drop folder for external repos or skill packs before
  import processing.
- `pgsa/imports/sources/<source_id>/`: an optional local copy of the imported
  source, used when the project wants the external material to be reviewable in
  the same repository.
- `external_import_review`: the default package-review session registered in
  `pgsa/sessions.yaml`, responsible for triaging imports and writing review
  artifacts before promotion.

Importing is intentionally review-first:

1. Add or copy the external source into `pgsa/imports/inbox/`.
2. Run `pgsa import process-inbox` to copy it into `pgsa/imports/sources/`,
   record it in `pgsa/imports/index.json`, and clear the processed inbox item.
3. Run `pgsa import review <source_id>` to scan the copied source, detect
   `SKILL.md`/README/schema files, update the index, write the review result
   into the import-review session summary/harness, and create a pending ledger
   event.
4. Use the default `external_import_review` session, or create a custom import
   session, to decide what should become PGSA state.
5. Promote only accepted content into contracts, session summaries, role files,
   capability manifests, or ledger decisions.

Do not treat imported content as trusted instructions by default. It is source
material for a session to inspect and integrate.

Optional tooling:

```bash
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import add external_pack --path ../external-pack --kind skill_pack
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import process-inbox
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import review external_pack
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . import stats
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root . session register external_skill_import --role external-skill-review --scope "triage imported skills" --must-read imports/index.json,imports/sources/external_pack/ --must-update state/external_skill_import.summary.md,ledger/pending/
```

End-to-end external verification:

```bash
python3 tools/scripts/verify_external_skill_imports.py
```

The verification script clones public external skill sources, drops them into a
temporary project's `pgsa/imports/inbox/`, runs `process-inbox`, runs
`import review` for each source, checks that the inbox is cleaned, checks that
review artifacts and pending ledger events exist, and validates the resulting
PGSA project.

This creates an explicit integration trail, not an automatic plugin loader.
Accepted import metadata can later be promoted into `pgsa/skills/`, role files,
contracts, capability manifests, or ledger decisions. Raw unreviewed external
content stays in `pgsa/imports/sources/<source_id>/`.

## Management Boundary

Keep these layers separate:

- bundled PGSA optional packs live in `protocol/capabilities/`,
  `protocol/adapters/`, `protocol/templates/`, and `protocol/schemas/`;
- user-added external material enters the target project through
  `pgsa/imports/inbox/` and, after processing, `pgsa/imports/sources/<source_id>/`;
- accepted skill metadata or provenance can be promoted into `pgsa/skills/`
  when advanced mode is used;
- raw unreviewed external content should not be copied directly into shipped
  `protocol/` folders.

The import layer is for organizing and reviewing external material. It does not
install skills into a user's global agent environment by itself.