from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class SessionAgentShimTests(unittest.TestCase):
    def run_pgsa(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "pgsa_cli.main", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env={"PYTHONPATH": str(ROOT / "tools" / "python")},
            check=False,
        )

    def test_creates_session_agent_folder_with_skill_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--advanced", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            created = self.run_pgsa("--root", temp_dir, "session-agent", "create", "backend")
            self.assertEqual(created.returncode, 0, created.stderr)
            payload = json.loads(created.stdout)
            self.assertEqual(payload["session"], "backend")

            agent_dir = Path(temp_dir) / "pgsa" / "session_agents" / "backend"
            descriptor = json.loads((agent_dir / "PGSA_SESSION.json").read_text(encoding="utf-8"))
            self.assertEqual(descriptor["session_id"], "backend")
            self.assertEqual(descriptor["session_registry"], "../../sessions.yaml")
            self.assertEqual(descriptor["accepted_skills_manifest"], "../../skills/signed_skill_manifest.yaml")
            self.assertIn("contracts/", descriptor["must_read"])

            agent_text = (agent_dir / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("PGSA Session Agent: backend", agent_text)
            self.assertIn("skills/signed_skill_manifest.yaml", agent_text)
            self.assertIn("Do not read or apply raw", agent_text)
            self.assertIn("external_import_review", agent_text)
            self.assertIn("created/maintained by the", agent_text)
            self.assertIn("Self-Maintenance", agent_text)

            skill_text = (agent_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: pgsa-session-backend", skill_text)
            self.assertIn("registered `backend` session", skill_text)
            self.assertIn("Skill Routing", skill_text)
            self.assertIn("<pgsa_root>/skills/signed_skill_manifest.yaml", skill_text)
            self.assertIn("applies_to", skill_text)

            validate = self.run_pgsa("--root", temp_dir, "validate", "--strict-advanced")
            self.assertEqual(validate.returncode, 0, validate.stdout)

    def test_can_create_sibling_session_folder(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            temp_dir = Path(base_dir) / "target-project"
            temp_dir.mkdir()
            init = self.run_pgsa("--root", str(temp_dir), "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            created = self.run_pgsa(
                "--root",
                str(temp_dir),
                "session-agent",
                "create",
                "frontend_components",
                "--out",
                "../agent-sessions/frontend_components",
                "--harness-root",
                "../pgsa-harness",
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            agent_dir = Path(base_dir) / "agent-sessions" / "frontend_components"
            descriptor = json.loads((agent_dir / "PGSA_SESSION.json").read_text(encoding="utf-8"))
            self.assertEqual(descriptor["session_id"], "frontend_components")
            self.assertTrue(descriptor["pgsa_root"].endswith("pgsa"))
            self.assertTrue(descriptor["harness_root"].endswith("pgsa-harness"))

            agent_text = (agent_dir / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("frontend_components", agent_text)
            self.assertIn("must_update", agent_text)


if __name__ == "__main__":
    unittest.main()
