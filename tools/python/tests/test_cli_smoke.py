from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pgsa_cli.cli import main as pgsa_main


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON_ROOT = REPO_ROOT / "tools" / "python"


class PGSACliSmokeTest(unittest.TestCase):
    def run_pgsa(self, *args: str) -> SimpleNamespace:
        stdout = io.StringIO()
        stderr = io.StringIO()
        previous_cwd = Path.cwd()
        os.chdir(REPO_ROOT)
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    code = pgsa_main(list(args))
                except SystemExit as exc:
                    code = exc.code if isinstance(exc.code, int) else 1
        finally:
            os.chdir(previous_cwd)
        return SimpleNamespace(returncode=int(code or 0), stdout=stdout.getvalue(), stderr=stderr.getvalue())

    def test_init_validate_and_drift_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            self.assertEqual(json.loads(validate.stdout), {"issues": []})

            drift = self.run_pgsa("--root", temp_dir, "drift-report")
            self.assertEqual(drift.returncode, 0, drift.stderr)
            self.assertTrue((Path(temp_dir) / "pgsa" / "reports" / "drift_report.json").exists())

            watch = self.run_pgsa("--root", temp_dir, "watch")
            self.assertEqual(watch.returncode, 0, watch.stderr)

            queue = self.run_pgsa("--root", temp_dir, "queue", "list")
            self.assertEqual(queue.returncode, 0, queue.stderr)

    def test_advanced_init_validate_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--advanced", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            self.assertEqual(json.loads(validate.stdout), {"issues": []})

            expected = [
                "pgsa/gates/verification_blueprint.yaml",
                "pgsa/gates/review_router.yaml",
                "pgsa/runtime/session_runtime_profile.yaml",
                "pgsa/runtime/capability_contract.yaml",
                "pgsa/skills/signed_skill_manifest.yaml",
                "pgsa/factory/factory_plan.yaml",
                "pgsa/scenarios/project.acceptance.v1.yaml",
                "pgsa/evidence/runtime_evidence.jsonl",
                "pgsa/audits/cognitive_audit_note.md",
            ]
            for rel in expected:
                self.assertTrue((Path(temp_dir) / rel).exists(), rel)

    def test_conflict_and_integration_blockers_are_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            merge = self.run_pgsa(
                "--root",
                temp_dir,
                "merge",
                "propose",
                "--session",
                "backend",
                "--sessions",
                "frontend_components",
                "--summary",
                "API response shape changed.",
            )
            self.assertEqual(merge.returncode, 0, merge.stderr)

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            issues = json.loads(validate.stdout)["issues"]
            self.assertTrue(any(issue["category"] == "unresolved_merge_conflicts" for issue in issues))

            integration_path = Path(temp_dir) / "pgsa" / "integration" / "integration_report.json"
            integration = json.loads(integration_path.read_text(encoding="utf-8"))
            integration["blocking_issues"] = ["frontend review pending"]
            integration_path.write_text(json.dumps(integration, indent=2) + "\n", encoding="utf-8")

            blocked = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(blocked.returncode, 1, blocked.stderr)
            issues = json.loads(blocked.stdout)["issues"]
            self.assertTrue(any(issue["category"] == "integration_failures" for issue in issues))

    def test_example_project_validates(self) -> None:
        validate = self.run_pgsa("--root", "examples/teamtask-projectboard", "validate")
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertEqual(json.loads(validate.stdout), {"issues": []})

    def test_embedded_folder_smoke_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            smoke = subprocess.run(
                ["sh", "tools/scripts/smoke_test.sh", temp_dir],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(smoke.returncode, 0, smoke.stderr)
            self.assertTrue((Path(temp_dir) / "pgsa-harness" / "protocol" / "SKILL.md").exists())
            self.assertTrue((Path(temp_dir) / "pgsa" / "sessions.yaml").exists())
            self.assertTrue((Path(temp_dir) / "backend_context.md").exists())


if __name__ == "__main__":
    unittest.main()
