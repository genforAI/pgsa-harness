#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_ROOT = REPO_ROOT / "tools" / "python"
DEFAULT_REPO_URL = "https://github.com/openai/skills.git"
DEFAULT_SKILLS = ["skills/.curated/cli-creator", "skills/.curated/openai-docs"]


def _run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "command failed:\n"
            + " ".join(command)
            + f"\nexit={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def _pgsa(project_root: Path, *args: str) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PYTHON_ROOT)
    result = _run(
        [sys.executable, "-m", "pgsa_cli.main", "--root", str(project_root), *args],
        cwd=REPO_ROOT,
        env=env,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"PGSA command did not return JSON: {result.stdout}") from exc


def _source_id(name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.:-]+", "_", name.strip())
    normalized = normalized.strip("._:-")
    return normalized or "external_source"


def _copy_skill_to_inbox(skills_repo: Path, project_root: Path, skill_rel: str) -> str:
    source = skills_repo / skill_rel
    if not source.exists():
        raise FileNotFoundError(f"missing sparse-checkout skill path: {skill_rel}")
    source_id = "openai_" + _source_id(source.name)
    destination = project_root / "pgsa" / "imports" / "inbox" / source_id
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return source_id


def _assert_import_review(project_root: Path, source_id: str) -> dict[str, Any]:
    pgsa = project_root / "pgsa"
    index = json.loads((pgsa / "imports" / "index.json").read_text(encoding="utf-8"))
    record = index["imports"][source_id]
    pending = pgsa / "ledger" / "pending" / f"import_review_{source_id}.json"
    local_path = record.get("local_path")
    local_root = pgsa / local_path if local_path else None
    detected = record.get("detected_skills", [])

    checks = {
        "status_reviewed": record.get("status") == "reviewed",
        "recommended_default_session": record.get("recommended_session") == "external_import_review",
        "local_source_exists": bool(local_root and local_root.exists()),
        "skill_detected": bool(detected),
        "pending_ledger_exists": pending.exists(),
        "inbox_cleaned": not (pgsa / "imports" / "inbox" / source_id).exists(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise AssertionError(f"import review checks failed for {source_id}: {failed}")

    return {
        "source_id": source_id,
        "status": record.get("status"),
        "kind": record.get("kind"),
        "local_path": local_path,
        "detected_skill_names": [skill.get("name") for skill in detected],
        "detected_skill_paths": [skill.get("path") for skill in detected],
        "pending_event_type": json.loads(pending.read_text(encoding="utf-8")).get("event_type"),
        "checks": checks,
    }


def verify(repo_url: str, skill_paths: list[str], keep_workdir: bool) -> dict[str, Any]:
    workdir_context = tempfile.TemporaryDirectory(prefix="pgsa-external-skill-import-")
    workdir = Path(workdir_context.name)
    try:
        project_root = workdir / "project"
        skills_repo = workdir / "skills-repo"

        _pgsa(project_root, "init", "--force")
        _run(
            ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", repo_url, str(skills_repo)],
            cwd=workdir,
        )
        _run(["git", "sparse-checkout", "set", *skill_paths], cwd=skills_repo)

        source_ids = [_copy_skill_to_inbox(skills_repo, project_root, skill_path) for skill_path in skill_paths]
        processed = _pgsa(project_root, "import", "process-inbox")
        if processed.get("processed_count") != len(source_ids):
            raise AssertionError(f"expected {len(source_ids)} processed imports, got {processed}")
        if not processed.get("cleaned"):
            raise AssertionError("process-inbox did not report cleaned=true")

        review_outputs = {}
        for source_id in source_ids:
            review_outputs[source_id] = _pgsa(
                project_root,
                "import",
                "review",
                source_id,
                "--summary",
                f"Verified external import workflow for {source_id}; source remains review-first and is not auto-activated.",
            )

        validate = _pgsa(project_root, "validate")
        if validate != {"issues": []}:
            raise AssertionError(f"validate returned issues: {validate}")

        context = _run(
            [
                sys.executable,
                "-m",
                "pgsa_cli.main",
                "--root",
                str(project_root),
                "export-context",
                "--session",
                "external_import_review",
            ],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": str(PYTHON_ROOT)},
        ).stdout
        if "external-import-review" not in context:
            raise AssertionError("external_import_review context did not include expected session role")

        import_summaries = [_assert_import_review(project_root, source_id) for source_id in source_ids]
        result = {
            "ok": True,
            "repo_url": repo_url,
            "skill_paths": skill_paths,
            "project_root": str(project_root) if keep_workdir else "<temporary>",
            "processed_count": processed.get("processed_count"),
            "validate": validate,
            "review_outputs": review_outputs,
            "imports": import_summaries,
        }
        if keep_workdir:
            workdir_context = None  # type: ignore[assignment]
        return result
    finally:
        if workdir_context is not None:
            workdir_context.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clone external skill sources and verify PGSA inbox -> review import behavior."
    )
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--skill", action="append", dest="skills", help="skill path inside the external repo")
    parser.add_argument("--keep-workdir", action="store_true", help="keep the temporary project for inspection")
    args = parser.parse_args()

    skills = args.skills or DEFAULT_SKILLS
    print(json.dumps(verify(args.repo_url, skills, args.keep_workdir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
