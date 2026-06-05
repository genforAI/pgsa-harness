from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from pgsa_core.io import read_structured, write_json
from pgsa_core.metrics.drift import drift_report, write_drift_report
from pgsa_core.supervisor.context import continuation_prompt, export_context, read_session_harness, record_session_event
from pgsa_core.templates.defaults import SESSION_HARNESS_TEMPLATE, SESSION_SUMMARY_TEMPLATE
from pgsa_core.templates.initializer import init_pgsa
from pgsa_core.validators.artifacts import issues_to_dicts, validate


def _apply_strict_advanced(issues):
    for issue in issues:
        if issue.category == "advanced_capability_state" and issue.severity == "warning":
            issue.severity = "error"
    return issues


def cmd_init(args: argparse.Namespace) -> int:
    written = init_pgsa(Path(args.root), force=args.force, advanced=args.advanced)
    print(json.dumps({"root": args.root, "written": [str(path) for path in written]}, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.root)
    issues = validate(root)
    report = drift_report(root)
    valid = not any(issue.severity == "error" for issue in issues)
    print(json.dumps({"valid": valid, "drift": report}, indent=2))
    return 0 if valid else 1


def cmd_validate(args: argparse.Namespace) -> int:
    issues = validate(Path(args.root))
    if args.strict_advanced:
        _apply_strict_advanced(issues)
    print(json.dumps({"issues": issues_to_dicts(issues)}, indent=2))
    return 0 if not any(issue.severity == "error" for issue in issues) else 1


def cmd_drift_report(args: argparse.Namespace) -> int:
    print(str(write_drift_report(Path(args.root))))
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    root = Path(args.root)
    issues = validate(root)
    report = drift_report(root)
    payload = {
        "watch_mode": "one_shot",
        "note": "watch is a convenience status check, not a background supervisor.",
        "valid": not any(issue.severity == "error" for issue in issues),
        "issues": issues_to_dicts(issues),
        "recommended_next_action": report["recommended_next_action"],
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["valid"] else 1


def cmd_queue_list(args: argparse.Namespace) -> int:
    root = Path(args.root)
    queue_path = root / "pgsa" / "tasks" / "queue.json"
    if queue_path.exists():
        tasks = json.loads(queue_path.read_text(encoding="utf-8"))
    else:
        tasks = []
    print(json.dumps({"queue": tasks, "note": "queue is optional; PGSA session communication uses repo-local artifacts"}, indent=2))
    return 0


def _write_or_print(text: str, output: str | None) -> int:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(str(path))
    else:
        print(text)
    return 0


def _split_csv_items(values: list[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for item in value.split(","):
            item = item.strip()
            if item:
                items.append(item)
    return items


def _session_scope_text(scope: list[str]) -> str:
    return "\n".join(f"- {item}" for item in scope) if scope else "- project work"


def cmd_session_register(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pgsa = root / "pgsa"
    sessions_path = pgsa / "sessions.yaml"
    if not sessions_path.exists():
        raise FileNotFoundError(f"missing sessions file: {sessions_path}")
    sessions_doc = read_structured(sessions_path)
    sessions = sessions_doc.setdefault("sessions", {})
    if args.session in sessions and not args.force:
        raise ValueError(f"session already exists: {args.session}; pass --force to replace it")

    owner_scope = _split_csv_items(args.scope) or [args.role]
    produces = _split_csv_items(args.produces) or [f"state/{args.session}.summary.md"]
    consumes = _split_csv_items(args.consumes)
    must_read = _split_csv_items(args.must_read) or [
        "project.yaml",
        "sessions.yaml",
        "contracts/",
        "state/",
        "merge_proposals/",
        "imports/index.json",
    ]
    must_update = _split_csv_items(args.must_update) or [
        f"harness/{args.session}.md",
        f"state/{args.session}.summary.md",
        "ledger/pending/",
    ]
    handoff_to = _split_csv_items(args.handoff_to)

    sessions[args.session] = {
        "role": args.role,
        "status": args.status,
        "owner_scope": owner_scope,
        "produces": produces,
        "consumes": consumes,
        "must_read": must_read,
        "must_update": must_update,
        "handoff_to": handoff_to,
        "registration": {
            "mode": "self_registered" if args.self_registered else "user_registered",
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "registered_by": args.registered_by,
            "notes": args.notes,
        },
        "escalation_policy": {
            "create_merge_proposal_when": [
                "this session changes a shared assumption",
                "imported content conflicts with existing project contracts",
                "consumer compatibility is unknown",
            ],
            "block_integration_when": ["required review or imported-source triage is missing"],
        },
    }
    write_json(sessions_path, sessions_doc)

    scope_text = _session_scope_text(owner_scope)
    summary = pgsa / "state" / f"{args.session}.summary.md"
    harness = pgsa / "harness" / f"{args.session}.md"
    if args.force or not summary.exists():
        summary.write_text(SESSION_SUMMARY_TEMPLATE.format(session=args.session, scope=scope_text), encoding="utf-8")
    if args.force or not harness.exists():
        harness.write_text(SESSION_HARNESS_TEMPLATE.format(session=args.session, scope=scope_text), encoding="utf-8")

    record_session_event(root, args.session, "SESSION_REGISTERED", args.status, ["sessions.yaml", str(summary.relative_to(pgsa)), str(harness.relative_to(pgsa))])
    print(json.dumps({"session": args.session, "role": args.role, "status": args.status, "summary": str(summary), "harness": str(harness)}, indent=2))
    return 0


def cmd_harness(args: argparse.Namespace) -> int:
    return _write_or_print(read_session_harness(Path(args.root), args.session), args.output)


def cmd_export_context(args: argparse.Namespace) -> int:
    return _write_or_print(export_context(Path(args.root), args.session), args.output)


def cmd_continuation_prompt(args: argparse.Namespace) -> int:
    return _write_or_print(continuation_prompt(Path(args.root), args.session), args.output)


def cmd_session_start(args: argparse.Namespace) -> int:
    root = Path(args.root)
    record_session_event(root, args.session, "SESSION_STARTED", "started", [])
    print(export_context(root, args.session))
    return 0


def cmd_session_update(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pgsa = root / "pgsa"
    summary = pgsa / "state" / f"{args.session}.summary.md"
    if args.notes:
        summary.parent.mkdir(parents=True, exist_ok=True)
        with summary.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## Update\n{args.notes}\n")
    record_session_event(root, args.session, "SESSION_UPDATED", "updated", [str(summary.relative_to(pgsa))])
    print(str(summary))
    return 0


def cmd_contract_diff(args: argparse.Namespace) -> int:
    issues = [issue for issue in validate(Path(args.root)) if issue.category == "contract_violations"]
    print(json.dumps({"contract_issues": issues_to_dicts(issues)}, indent=2))
    return 0 if not issues else 1


def cmd_integration_check(args: argparse.Namespace) -> int:
    issues = [issue for issue in validate(Path(args.root)) if issue.category == "integration_failures"]
    print(json.dumps({"integration_issues": issues_to_dicts(issues)}, indent=2))
    return 0 if not issues else 1


def cmd_merge_propose(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pgsa = root / "pgsa"
    merge_dir = pgsa / "merge_proposals"
    merge_dir.mkdir(parents=True, exist_ok=True)
    next_id = len(sorted(merge_dir.glob("mp_*.md"))) + 1
    path = merge_dir / f"mp_{next_id:03d}.md"
    path.write_text(
        f"""# Merge Proposal MP-{next_id:03d}

status: open
conflict_type: {args.conflict_type}
decision_owner: {args.decision_owner}
producer_session: {args.session}
consumer_sessions: {args.sessions}
changed_contracts: {args.contracts}
affected_files: {args.files}
created_at: pending
updated_at: pending

## Conflict Summary

{args.summary}

## Evidence

- Contract before:
- Contract after:
- Producer change:
- Consumer impact:

## Resolution Options
1. Update affected consumers.
2. Add compatibility adapter.
3. Revise the contract.
4. Revert the producer change.

## Selected Resolution

pending

## Review Requirements

- producer accepted: no
- consumers accepted: no
- integration accepted: no

## Integration Readiness
blocked_until_reviewed
""",
        encoding="utf-8",
    )
    record_session_event(root, args.session, "MERGE_PROPOSAL_CREATED", "requires_review", [str(path.relative_to(pgsa))])
    print(str(path))
    return 0


def _scan_import_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    ignored_dirs = {".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv"}
    ignored_files = {".DS_Store"}
    files: list[Path] = []
    for child in sorted(path.rglob("*")):
        rel_parts = set(child.relative_to(path).parts)
        if rel_parts & ignored_dirs:
            continue
        if child.name in ignored_files:
            continue
        if child.is_file():
            files.append(child)
    return files


def _copy_import_source(source: Path, destination: Path, force: bool) -> None:
    if destination.exists():
        if not force:
            raise FileExistsError(f"import destination exists: {destination}; pass --force to replace it")
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv", ".DS_Store"),
        )
    else:
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination / source.name)


def _read_import_index(pgsa: Path) -> dict:
    index_path = pgsa / "imports" / "index.json"
    if not index_path.exists():
        return {"version": "1.0", "imports": {}, "notes": []}
    return read_structured(index_path)


def _source_id_from_name(name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.:-]+", "_", name.strip())
    normalized = normalized.strip("._:-")
    return normalized or "external_source"


def _unique_source_id(imports: dict, source_id: str) -> str:
    if source_id not in imports:
        return source_id
    index = 2
    while f"{source_id}_{index}" in imports:
        index += 1
    return f"{source_id}_{index}"


def _index_import_source(
    *,
    root: Path,
    source_id: str,
    source: Path,
    kind: str,
    session: str,
    notes: str,
    no_copy: bool,
    force: bool,
    max_listed_files: int,
) -> dict:
    pgsa = root / "pgsa"
    source = source.expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"import source does not exist: {source}")

    index = _read_import_index(pgsa)
    imports = index.setdefault("imports", {})
    if source_id in imports and not force:
        raise ValueError(f"import source already exists: {source_id}; pass --force to replace it")

    destination_rel = f"imports/sources/{source_id}"
    destination = pgsa / destination_rel
    local_path = None
    if not no_copy:
        _copy_import_source(source, destination, force)
        local_path = destination_rel

    scan_root = destination if local_path else source
    files = _scan_import_files(scan_root)
    selected_files = [str(file.relative_to(scan_root)) for file in files[:max_listed_files]]
    total_bytes = sum(file.stat().st_size for file in files)
    imports[source_id] = {
        "kind": kind,
        "status": "indexed",
        "origin_path": str(source),
        "local_path": local_path,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "recommended_session": session,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "selected_files": selected_files,
        "notes": notes,
    }
    write_json(pgsa / "imports" / "index.json", index)
    record_session_event(root, session, "IMPORT_INDEXED", "indexed", ["imports/index.json"] + ([destination_rel] if local_path else []))
    return {"source_id": source_id, "file_count": len(files), "total_bytes": total_bytes, "local_path": local_path}


def _read_skill_metadata(skill_path: Path, source_root: Path) -> dict[str, str]:
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    metadata: dict[str, str] = {}
    if text.startswith("---"):
        lines = text.splitlines()
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in {"name", "description"}:
                metadata[key] = value
    return {
        "name": metadata.get("name") or skill_path.parent.name,
        "description": metadata.get("description", ""),
        "path": str(skill_path.relative_to(source_root)),
    }


def _detect_import_capabilities(source_root: Path, max_skills: int) -> dict:
    files = _scan_import_files(source_root)
    skill_paths = [path for path in files if path.name == "SKILL.md"]
    readmes = [path for path in files if path.name.lower() in {"readme.md", "readme.txt"}]
    schemas = [path for path in files if path.suffix.lower() in {".schema.json", ".schema.yaml", ".schema.yml"}]
    return {
        "skill_count": len(skill_paths),
        "skills": [_read_skill_metadata(path, source_root) for path in skill_paths[:max_skills]],
        "readme_count": len(readmes),
        "schema_count": len(schemas),
    }


def _append_import_review_markdown(path: Path, source_id: str, source: dict, capabilities: dict, summary: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    skills = capabilities.get("skills", [])
    skill_lines = "\n".join(
        f"- `{skill.get('name')}` from `{Path(skill.get('path', '')).name}`: {skill.get('description') or 'no description'}"
        for skill in skills
    ) or "- No `SKILL.md` files detected."
    path.write_text(
        path.read_text(encoding="utf-8") if path.exists() else "",
        encoding="utf-8",
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"""

## Import Review: {source_id}

- status: {source.get('status')}
- kind: {source.get('kind')}
- local_path: {source.get('local_path')}
- detected_skill_count: {capabilities.get('skill_count', 0)}
- readme_count: {capabilities.get('readme_count', 0)}
- schema_count: {capabilities.get('schema_count', 0)}

### Detected Skills
{skill_lines}

### Review Summary
{summary}
"""
        )


def cmd_import_review(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pgsa = root / "pgsa"
    index = _read_import_index(pgsa)
    imports = index.setdefault("imports", {})
    if args.source_id not in imports:
        raise KeyError(f"unknown import source: {args.source_id}")

    item = imports[args.source_id]
    session = args.session or item.get("recommended_session") or "external_import_review"
    local_path = item.get("local_path")
    if local_path:
        source_root = pgsa / local_path
    else:
        origin_path = item.get("origin_path")
        if not origin_path:
            raise ValueError(f"import {args.source_id} has no local_path or origin_path")
        source_root = Path(origin_path)
    if not source_root.exists():
        raise FileNotFoundError(f"import source missing: {source_root}")

    capabilities = _detect_import_capabilities(source_root, args.max_skills)
    summary = args.summary or (
        f"Reviewed {args.source_id}: detected {capabilities['skill_count']} SKILL.md file(s), "
        f"{capabilities['readme_count']} README file(s), and {capabilities['schema_count']} schema file(s)."
    )
    reviewed_at = datetime.now(timezone.utc).isoformat()
    review_artifacts = [
        f"harness/{session}.md",
        f"state/{session}.summary.md",
        f"ledger/pending/import_review_{_source_id_from_name(args.source_id)}.json",
    ]

    item.update(
        {
            "status": args.status,
            "reviewed_at": reviewed_at,
            "review_session": session,
            "review_summary": summary,
            "review_artifacts": review_artifacts,
            "detected_skills": capabilities["skills"],
        }
    )
    write_json(pgsa / "imports" / "index.json", index)

    harness = pgsa / "harness" / f"{session}.md"
    summary_path = pgsa / "state" / f"{session}.summary.md"
    _append_import_review_markdown(harness, args.source_id, item, capabilities, summary)
    _append_import_review_markdown(summary_path, args.source_id, item, capabilities, summary)

    pending = pgsa / "ledger" / "pending" / f"import_review_{_source_id_from_name(args.source_id)}.json"
    write_json(
        pending,
        {
            "event_id": f"pending_import_review_{_source_id_from_name(args.source_id)}",
            "timestamp": reviewed_at,
            "event_type": "IMPORT_REVIEWED",
            "session": session,
            "status": args.status,
            "artifact_refs": ["imports/index.json", *review_artifacts],
            "source_id": args.source_id,
            "detected_skill_count": capabilities["skill_count"],
            "summary": summary,
        },
    )
    record_session_event(root, session, "IMPORT_REVIEWED", args.status, ["imports/index.json", *review_artifacts])
    print(
        json.dumps(
            {
                "source_id": args.source_id,
                "status": args.status,
                "session": session,
                "detected_skill_count": capabilities["skill_count"],
                "review_artifacts": review_artifacts,
            },
            indent=2,
        )
    )
    return 0


def cmd_import_add(args: argparse.Namespace) -> int:
    result = _index_import_source(
        root=Path(args.root),
        source_id=args.source_id,
        source=Path(args.path),
        kind=args.kind,
        session=args.session,
        notes=args.notes,
        no_copy=args.no_copy,
        force=args.force,
        max_listed_files=args.max_listed_files,
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_import_process_inbox(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pgsa = root / "pgsa"
    inbox = Path(args.inbox)
    if not inbox.is_absolute():
        inbox = pgsa / inbox
    inbox.mkdir(parents=True, exist_ok=True)

    index = _read_import_index(pgsa)
    imports = index.setdefault("imports", {})
    processed = []
    skipped = []
    for source in sorted(inbox.iterdir()):
        if source.name.startswith(".") or source.name == "README.md":
            skipped.append(str(source))
            continue
        source_id = args.source_id_prefix + _source_id_from_name(source.name)
        if not args.force:
            source_id = _unique_source_id(imports, source_id)
        result = _index_import_source(
            root=root,
            source_id=source_id,
            source=source,
            kind=args.kind,
            session=args.session,
            notes=args.notes or f"Processed from import inbox: {source.name}",
            no_copy=False,
            force=args.force,
            max_listed_files=args.max_listed_files,
        )
        processed.append(result)
        if not args.keep:
            if source.is_dir():
                shutil.rmtree(source)
            else:
                source.unlink()

    print(
        json.dumps(
            {
                "inbox": str(inbox),
                "processed_count": len(processed),
                "processed": processed,
                "skipped": skipped,
                "cleaned": not args.keep,
            },
            indent=2,
        )
    )
    return 0


def cmd_import_stats(args: argparse.Namespace) -> int:
    pgsa = Path(args.root) / "pgsa"
    index = _read_import_index(pgsa)
    imports = index.get("imports", {})
    by_kind: dict[str, int] = {}
    total_files = 0
    total_bytes = 0
    for item in imports.values():
        kind = str(item.get("kind", "unknown"))
        by_kind[kind] = by_kind.get(kind, 0) + 1
        total_files += int(item.get("file_count", 0) or 0)
        total_bytes += int(item.get("total_bytes", 0) or 0)
    print(json.dumps({"source_count": len(imports), "by_kind": by_kind, "total_files": total_files, "total_bytes": total_bytes}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pgsa")
    parser.add_argument("--root", default=".", help="project root containing or receiving pgsa/")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--force", action="store_true")
    p.add_argument("--advanced", action="store_true", help="initialize optional advanced capability artifacts")
    p.set_defaults(func=cmd_init)

    sub.add_parser("status").set_defaults(func=cmd_status)
    p = sub.add_parser("validate")
    p.add_argument("--strict-advanced", action="store_true", help="treat optional advanced artifact warnings as errors")
    p.set_defaults(func=cmd_validate)
    sub.add_parser("drift-report").set_defaults(func=cmd_drift_report)
    sub.add_parser("watch").set_defaults(func=cmd_watch)

    p = sub.add_parser("harness")
    p.add_argument("--session", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_harness)

    p = sub.add_parser("export-context")
    p.add_argument("--session", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_export_context)

    p = sub.add_parser("continuation-prompt")
    p.add_argument("--session", required=True)
    p.add_argument("--output")
    p.set_defaults(func=cmd_continuation_prompt)

    session = sub.add_parser("session")
    session_sub = session.add_subparsers(dest="session_command", required=True)
    p = session_sub.add_parser("start")
    p.add_argument("session")
    p.set_defaults(func=cmd_session_start)
    p = session_sub.add_parser("update")
    p.add_argument("session")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_session_update)
    p = session_sub.add_parser("register")
    p.add_argument("session")
    p.add_argument("--role", required=True)
    p.add_argument("--status", default="active")
    p.add_argument("--scope", action="append", help="owner scope item; comma-separated values are also accepted")
    p.add_argument("--produces", action="append", help="produced artifact path; comma-separated values are also accepted")
    p.add_argument("--consumes", action="append", help="consumed artifact path; comma-separated values are also accepted")
    p.add_argument("--must-read", action="append", help="required read artifact path; comma-separated values are also accepted")
    p.add_argument("--must-update", action="append", help="required update artifact path; comma-separated values are also accepted")
    p.add_argument("--handoff-to", action="append", help="handoff target session; comma-separated values are also accepted")
    p.add_argument("--registered-by", default="user")
    p.add_argument("--notes", default="")
    p.add_argument("--self-registered", action="store_true")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_session_register)

    contract = sub.add_parser("contract")
    contract_sub = contract.add_subparsers(dest="contract_command", required=True)
    contract_sub.add_parser("diff").set_defaults(func=cmd_contract_diff)

    integration = sub.add_parser("integration")
    integration_sub = integration.add_subparsers(dest="integration_command", required=True)
    integration_sub.add_parser("check").set_defaults(func=cmd_integration_check)

    merge = sub.add_parser("merge")
    merge_sub = merge.add_subparsers(dest="merge_command", required=True)
    p = merge_sub.add_parser("propose")
    p.add_argument("--session", required=True)
    p.add_argument("--sessions", required=True)
    p.add_argument("--contracts", default="contracts/api.project.v1.json")
    p.add_argument("--files", default="")
    p.add_argument("--decision-owner", default="docs_security_integration")
    p.add_argument("--conflict-type", default="semantic_conflict")
    p.add_argument("--summary", default="Potential project-level conflict.")
    p.set_defaults(func=cmd_merge_propose)

    imports = sub.add_parser("import")
    imports_sub = imports.add_subparsers(dest="import_command", required=True)
    p = imports_sub.add_parser("add")
    p.add_argument("source_id")
    p.add_argument("--path", required=True)
    p.add_argument("--kind", default="external_harness", choices=["external_harness", "skill_pack", "protocol", "docs", "other"])
    p.add_argument("--session", default="external_import_review")
    p.add_argument("--notes", default="")
    p.add_argument("--no-copy", action="store_true", help="index source in place instead of copying it into pgsa/imports/sources/")
    p.add_argument("--force", action="store_true")
    p.add_argument("--max-listed-files", type=int, default=200)
    p.set_defaults(func=cmd_import_add)
    p = imports_sub.add_parser("process-inbox")
    p.add_argument("--inbox", default="imports/inbox", help="inbox path relative to pgsa/ unless absolute")
    p.add_argument("--kind", default="skill_pack", choices=["external_harness", "skill_pack", "protocol", "docs", "other"])
    p.add_argument("--session", default="external_import_review")
    p.add_argument("--notes", default="")
    p.add_argument("--keep", action="store_true", help="keep inbox sources after indexing")
    p.add_argument("--force", action="store_true")
    p.add_argument("--source-id-prefix", default="")
    p.add_argument("--max-listed-files", type=int, default=200)
    p.set_defaults(func=cmd_import_process_inbox)
    p = imports_sub.add_parser("review")
    p.add_argument("source_id")
    p.add_argument("--session", default=None)
    p.add_argument("--status", default="reviewed", choices=["triaging", "reviewed", "accepted", "rejected", "deprecated"])
    p.add_argument("--summary", default="")
    p.add_argument("--max-skills", type=int, default=50)
    p.set_defaults(func=cmd_import_review)
    imports_sub.add_parser("stats").set_defaults(func=cmd_import_stats)

    queue = sub.add_parser("queue")
    queue_sub = queue.add_subparsers(dest="queue_command", required=True)
    queue_sub.add_parser("list").set_defaults(func=cmd_queue_list)

    return parser


def _normalize_global_options(argv: list[str]) -> list[str]:
    """Allow global --root before or after the subcommand."""
    normalized = list(argv)
    extracted: list[str] = []
    index = 0
    while index < len(normalized):
        item = normalized[index]
        if item == "--root" and index + 1 < len(normalized):
            extracted.extend([item, normalized[index + 1]])
            del normalized[index : index + 2]
            continue
        if item.startswith("--root="):
            extracted.append(item)
            del normalized[index]
            continue
        index += 1
    return extracted + normalized


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    normalized = _normalize_global_options(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(normalized)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
