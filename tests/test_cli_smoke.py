from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PGSACliSmokeTest(unittest.TestCase):
    def run_pgsa(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "pgsa_cli.main", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

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

    def test_example_project_validates(self) -> None:
        validate = self.run_pgsa("--root", "examples/teamtask-projectboard", "validate")
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertEqual(json.loads(validate.stdout), {"issues": []})


if __name__ == "__main__":
    unittest.main()
