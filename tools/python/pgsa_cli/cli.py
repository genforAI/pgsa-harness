from __future__ import annotations

import argparse
import json
from pathlib import Path

from pgsa_core.metrics.drift import drift_report, write_drift_report
from pgsa_core.supervisor.context import continuation_prompt, export_context, read_session_harness, record_session_event
from pgsa_core.templates.initializer import init_pgsa
from pgsa_core.validators.artifacts import issues_to_dicts, validate


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pgsa")
    parser.add_argument("--root", default=".", help="project root containing or receiving pgsa/")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--force", action="store_true")
    p.add_argument("--advanced", action="store_true", help="initialize optional advanced capability artifacts")
    p.set_defaults(func=cmd_init)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
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

    queue = sub.add_parser("queue")
    queue_sub = queue.add_subparsers(dest="queue_command", required=True)
    queue_sub.add_parser("list").set_defaults(func=cmd_queue_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
