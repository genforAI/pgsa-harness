from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class ImportPromoteTests(unittest.TestCase):
    def run_pgsa(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "pgsa_cli.main", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env={"PYTHONPATH": str(ROOT / "tools" / "python")},
            check=False,
        )

    def test_reviewed_import_can_promote_provenance_to_multiple_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--advanced", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            pgsa = Path(temp_dir) / "pgsa"
            inbox_source = pgsa / "imports" / "inbox" / "external_demo"
            inbox_source.mkdir(parents=True)
            (inbox_source / "SKILL.md").write_text(
                """---
name: imported-demo-skill
description: Demo external skill for PGSA import promotion.
---

# Imported Demo Skill
""",
                encoding="utf-8",
            )

            processed = self.run_pgsa("--root", temp_dir, "import", "process-inbox")
            self.assertEqual(processed.returncode, 0, processed.stderr)
            source_id = json.loads(processed.stdout)["processed"][0]["source_id"]

            reviewed = self.run_pgsa("--root", temp_dir, "import", "review", source_id)
            self.assertEqual(reviewed.returncode, 0, reviewed.stderr)

            promoted = self.run_pgsa(
                "--root",
                temp_dir,
                "import",
                "promote",
                source_id,
                "--accept-import",
                "--applies-to",
                "backend,frontend_components,docs_security_integration",
            )
            self.assertEqual(promoted.returncode, 0, promoted.stderr)
            payload = json.loads(promoted.stdout)
            self.assertEqual(payload["applies_to"], ["backend", "frontend_components", "docs_security_integration"])
            self.assertTrue(payload["accepted"])

            manifest = json.loads((pgsa / "skills" / "signed_skill_manifest.yaml").read_text(encoding="utf-8"))
            promoted_skill = manifest["skills"][-1]
            self.assertEqual(promoted_skill["source_id"], source_id)
            self.assertEqual(promoted_skill["imported_skill_name"], "imported-demo-skill")
            self.assertEqual(promoted_skill["applies_to"], ["backend", "frontend_components", "docs_security_integration"])

            index = json.loads((pgsa / "imports" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["imports"][source_id]["status"], "accepted")
            self.assertEqual(index["imports"][source_id]["promoted_skill_ids"], [promoted_skill["skill_id"]])

            validate = self.run_pgsa("--root", temp_dir, "validate", "--strict-advanced")
            self.assertEqual(validate.returncode, 0, validate.stdout)
            self.assertEqual(json.loads(validate.stdout), {"issues": []})


if __name__ == "__main__":
    unittest.main()
