from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pgsa_cli import cli as base
from pgsa_core.io import read_structured, write_json
from pgsa_core.supervisor.context import record_session_event


def _artifact_id_from_name(name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.:]+", "_", name.strip()).strip("._:")
    if not normalized or not re.match(r"^[A-Za-z]", normalized):
        normalized = f"imported_{normalized or 'source'}"
    return normalized


def _read_skill_manifest(path: Path) -> dict[str, Any]:
    if path.exists():
        return read_structured(path)
    return {"manifest_id": "project.skills.v1", "skills": []}


def _promoted_skill_entries(
    *,
    source_id: str,
    item: dict[str, Any],
    applies_to: list[str],
    status: str,
    risk: str,
    signed_by: str,
    version: str,
    promoted_at: str,
    notes: str,
) -> list[dict[str, Any]]:
    detected = item.get("detected_skills") if isinstance(item.get("detected_skills"), list) else []
    skills = [skill for skill in detected if isinstance(skill, dict)] or [
        {"name": source_id, "path": item.get("local_path") or item.get("origin_path") or source_id}
    ]
    entries: list[dict[str, Any]] = []
    for skill in skills:
        name = str(skill.get("name") or source_id)
        path = str(skill.get("path") or item.get("local_path") or source_id)
        entries.append(
            {
                "skill_id": f"imported.{_artifact_id_from_name(source_id)}.{_artifact_id_from_name(name)}",
                "version": version,
                "status": status,
                "risk": risk,
                "applies_to": applies_to,
                "signed_by": signed_by,
                "depends_on": [
                    "imports/index.json",
                    *[ref for ref in [item.get("local_path")] if isinstance(ref, str) and ref],
                ],
                "source_id": source_id,
                "source_kind": item.get("kind"),
                "source_status": item.get("status"),
                "imported_skill_name": name,
                "imported_skill_path": path,
                "review_artifacts": item.get("review_artifacts", []),
                "promoted_at": promoted_at,
                "promotion_note": notes,
            }
        )
    return entries


def cmd_import_promote(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pgsa = root / "pgsa"
    index = base._read_import_index(pgsa)
    imports = index.setdefault("imports", {})
    if args.source_id not in imports:
        raise KeyError(f"unknown import source: {args.source_id}")

    item = imports[args.source_id]
    if item.get("status") not in {"reviewed", "accepted"} and not args.force:
        raise ValueError(
            f"import {args.source_id} must be reviewed or accepted before promotion; pass --force to override"
        )

    session = args.session or item.get("review_session") or item.get("recommended_session") or "external_import_review"
    applies_to = base._split_csv_items(args.applies_to) or [session]
    promoted_at = datetime.now(timezone.utc).isoformat()
    skills_path = pgsa / "skills" / "signed_skill_manifest.yaml"
    skills_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = _read_skill_manifest(skills_path)
    skills = manifest.setdefault("skills", [])
    if not isinstance(skills, list):
        raise ValueError(f"skills manifest has non-list skills field: {skills_path}")

    entries = _promoted_skill_entries(
        source_id=args.source_id,
        item=item,
        applies_to=applies_to,
        status=args.status,
        risk=args.risk,
        signed_by=args.signed_by,
        version=args.version,
        promoted_at=promoted_at,
        notes=args.notes,
    )
    existing_ids = {
        skill.get("skill_id"): index
        for index, skill in enumerate(skills)
        if isinstance(skill, dict)
    }
    promoted_ids: list[str] = []
    for entry in entries:
        skill_id = entry["skill_id"]
        if skill_id in existing_ids:
            if not args.force:
                raise ValueError(f"promoted skill already exists: {skill_id}; pass --force to replace it")
            skills[existing_ids[skill_id]] = entry
        else:
            skills.append(entry)
        promoted_ids.append(skill_id)

    write_json(skills_path, manifest)
    item.update(
        {
            "status": "accepted" if args.accept_import else item.get("status"),
            "promoted_at": promoted_at,
            "promoted_session": session,
            "promotion_artifacts": ["skills/signed_skill_manifest.yaml", "imports/index.json"],
            "promoted_skill_ids": promoted_ids,
        }
    )
    write_json(pgsa / "imports" / "index.json", index)
    record_session_event(
        root,
        session,
        "IMPORT_PROMOTED",
        "accepted" if args.accept_import else args.status,
        ["imports/index.json", "skills/signed_skill_manifest.yaml"],
    )
    print(
        base.json.dumps(
            {
                "source_id": args.source_id,
                "session": session,
                "applies_to": applies_to,
                "skills_manifest": "skills/signed_skill_manifest.yaml",
                "promoted_skill_ids": promoted_ids,
                "accepted": bool(args.accept_import),
            },
            indent=2,
        )
    )
    return 0


def _add_promote_parser(parser: argparse.ArgumentParser) -> None:
    subparsers = next(
        action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
    )
    import_parser = subparsers.choices.get("import")
    if import_parser is None:
        return
    import_subparsers = next(
        action for action in import_parser._actions if isinstance(action, argparse._SubParsersAction)
    )
    if "promote" in import_subparsers.choices:
        return

    promote = import_subparsers.add_parser("promote")
    promote.add_argument("source_id")
    promote.add_argument("--session", default=None)
    promote.add_argument("--status", default="active", choices=["active", "draft", "deprecated", "disabled"])
    promote.add_argument("--risk", default="medium", choices=["low", "medium", "high", "critical"])
    promote.add_argument("--signed-by", default="external_import_review")
    promote.add_argument("--version", default="1.0.0")
    promote.add_argument(
        "--applies-to",
        action="append",
        help="session(s) allowed to use this promoted provenance; comma-separated values are accepted",
    )
    promote.add_argument("--notes", default="")
    promote.add_argument("--accept-import", action="store_true", help="mark the import record accepted while promoting metadata")
    promote.add_argument("--force", action="store_true")
    promote.set_defaults(func=cmd_import_promote)


def install() -> None:
    original = base.build_parser

    if getattr(original, "_pgsa_promote_shim_installed", False):
        return

    def wrapped_build_parser() -> argparse.ArgumentParser:
        parser = original()
        _add_promote_parser(parser)
        return parser

    wrapped_build_parser._pgsa_promote_shim_installed = True  # type: ignore[attr-defined]
    base.build_parser = wrapped_build_parser
