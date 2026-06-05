from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pgsa_cli.cli import main as pgsa_main


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON_ROOT = REPO_ROOT / "tools" / "python"


def _schema_type_ok(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return True


def _assert_schema_subset(value: object, schema: dict[str, object], path: str = "$") -> None:
    if "anyOf" in schema:
        failures = []
        for option in schema["anyOf"]:  # type: ignore[index]
            try:
                _assert_schema_subset(value, option, path)
                return
            except AssertionError as exc:
                failures.append(str(exc))
        raise AssertionError(f"{path} did not match anyOf: {failures}")
    if "const" in schema:
        assert value == schema["const"], f"{path} should equal {schema['const']!r}"
    if "type" in schema:
        assert _schema_type_ok(value, schema["type"]), f"{path} should be {schema['type']}"  # type: ignore[arg-type]
    if "enum" in schema:
        assert value in schema["enum"], f"{path} should be one of {schema['enum']}"  # type: ignore[operator]
    if "pattern" in schema and isinstance(value, str):
        assert re.match(schema["pattern"], value), f"{path} does not match {schema['pattern']}"  # type: ignore[arg-type]
    if "minLength" in schema and isinstance(value, str):
        assert len(value) >= schema["minLength"], f"{path} shorter than minLength"  # type: ignore[operator]
    if isinstance(value, dict):
        required = schema.get("required", [])
        for field in required:  # type: ignore[union-attr]
            assert field in value, f"{path}.{field} is required"
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for field, field_schema in properties.items():
                if field in value:
                    _assert_schema_subset(value[field], field_schema, f"{path}.{field}")  # type: ignore[arg-type]
        additional = schema.get("additionalProperties", True)
        if isinstance(additional, dict):
            for field, field_value in value.items():
                if not isinstance(properties, dict) or field not in properties:
                    _assert_schema_subset(field_value, additional, f"{path}.{field}")  # type: ignore[arg-type]
        if "minProperties" in schema:
            assert len(value) >= schema["minProperties"], f"{path} has too few properties"  # type: ignore[operator]
    if isinstance(value, list):
        if "minItems" in schema:
            assert len(value) >= schema["minItems"], f"{path} has too few items"  # type: ignore[operator]
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _assert_schema_subset(item, item_schema, f"{path}[{index}]")


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "missing frontmatter"
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    raise AssertionError("unterminated frontmatter")


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

    def test_root_argument_after_subcommand(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("init", "--root", temp_dir, "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            validate = self.run_pgsa("validate", "--root", temp_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)
            self.assertEqual(json.loads(validate.stdout), {"issues": []})

    def test_session_register_creates_scoped_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            register = self.run_pgsa(
                "--root",
                temp_dir,
                "session",
                "register",
                "research_import",
                "--role",
                "external-skill-review",
                "--scope",
                "triage imported skills",
                "--must-read",
                "imports/index.json",
                "--must-update",
                "state/research_import.summary.md,ledger/pending/",
                "--handoff-to",
                "docs_security_integration",
                "--self-registered",
            )
            self.assertEqual(register.returncode, 0, register.stderr)
            pgsa = Path(temp_dir) / "pgsa"
            sessions = json.loads((pgsa / "sessions.yaml").read_text(encoding="utf-8"))
            self.assertEqual(sessions["sessions"]["research_import"]["role"], "external-skill-review")
            self.assertTrue((pgsa / "harness" / "research_import.md").exists())
            self.assertTrue((pgsa / "state" / "research_import.summary.md").exists())

            context = self.run_pgsa("--root", temp_dir, "export-context", "--session", "research_import")
            self.assertEqual(context.returncode, 0, context.stderr)
            self.assertIn("external-skill-review", context.stdout)

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stdout)

    def test_import_add_indexes_external_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as source_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            register = self.run_pgsa(
                "--root",
                temp_dir,
                "session",
                "register",
                "research_import",
                "--role",
                "external-skill-review",
                "--scope",
                "triage imported skills",
                "--force",
            )
            self.assertEqual(register.returncode, 0, register.stderr)

            source = Path(source_dir)
            (source / "skills").mkdir()
            (source / "skills" / "reader.md").write_text("# Reader skill\n", encoding="utf-8")
            (source / "README.md").write_text("external pack\n", encoding="utf-8")

            added = self.run_pgsa(
                "--root",
                temp_dir,
                "import",
                "add",
                "external_pack",
                "--path",
                source_dir,
                "--kind",
                "skill_pack",
                "--session",
                "research_import",
            )
            self.assertEqual(added.returncode, 0, added.stderr)
            payload = json.loads(added.stdout)
            self.assertEqual(payload["file_count"], 2)
            self.assertEqual(payload["local_path"], "imports/sources/external_pack")

            stats = self.run_pgsa("--root", temp_dir, "import", "stats")
            self.assertEqual(stats.returncode, 0, stats.stderr)
            stats_payload = json.loads(stats.stdout)
            self.assertEqual(stats_payload["source_count"], 1)
            self.assertEqual(stats_payload["by_kind"], {"skill_pack": 1})

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stdout)

    def test_default_import_session_processes_and_cleans_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            pgsa = Path(temp_dir) / "pgsa"
            sessions = json.loads((pgsa / "sessions.yaml").read_text(encoding="utf-8"))
            self.assertIn("external_import_review", sessions["sessions"])

            inbox_source = pgsa / "imports" / "inbox" / "external-skill-pack"
            (inbox_source / "skills").mkdir(parents=True)
            (inbox_source / "skills" / "importer.md").write_text("# Importer skill\n", encoding="utf-8")
            (inbox_source / "README.md").write_text("external import source\n", encoding="utf-8")

            processed = self.run_pgsa("--root", temp_dir, "import", "process-inbox")
            self.assertEqual(processed.returncode, 0, processed.stderr)
            payload = json.loads(processed.stdout)
            self.assertEqual(payload["processed_count"], 1)
            self.assertTrue(payload["cleaned"])
            self.assertFalse(inbox_source.exists())

            source_id = payload["processed"][0]["source_id"]
            self.assertTrue((pgsa / "imports" / "sources" / source_id / "skills" / "importer.md").exists())
            index = json.loads((pgsa / "imports" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["imports"][source_id]["recommended_session"], "external_import_review")

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stdout)

    def test_import_review_records_skill_triage_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            pgsa = Path(temp_dir) / "pgsa"
            inbox_source = pgsa / "imports" / "inbox" / "external-codex-skill"
            inbox_source.mkdir(parents=True)
            (inbox_source / "SKILL.md").write_text(
                """---
name: external-review-skill
description: Reviews imported external skill packs before project activation.
---

# External Review Skill
""",
                encoding="utf-8",
            )
            (inbox_source / "README.md").write_text("external skill pack\n", encoding="utf-8")

            processed = self.run_pgsa("--root", temp_dir, "import", "process-inbox")
            self.assertEqual(processed.returncode, 0, processed.stderr)
            source_id = json.loads(processed.stdout)["processed"][0]["source_id"]

            reviewed = self.run_pgsa("--root", temp_dir, "import", "review", source_id)
            self.assertEqual(reviewed.returncode, 0, reviewed.stderr)
            review_payload = json.loads(reviewed.stdout)
            self.assertEqual(review_payload["status"], "reviewed")
            self.assertEqual(review_payload["detected_skill_count"], 1)

            index = json.loads((pgsa / "imports" / "index.json").read_text(encoding="utf-8"))
            record = index["imports"][source_id]
            self.assertEqual(record["status"], "reviewed")
            self.assertEqual(record["detected_skills"][0]["name"], "external-review-skill")
            self.assertEqual(record["detected_skills"][0]["path"], "SKILL.md")

            summary = (pgsa / "state" / "external_import_review.summary.md").read_text(encoding="utf-8")
            harness = (pgsa / "harness" / "external_import_review.md").read_text(encoding="utf-8")
            self.assertIn("Import Review", summary)
            self.assertIn("external-review-skill", harness)
            pending = pgsa / "ledger" / "pending" / f"import_review_{source_id}.json"
            self.assertTrue(pending.exists())
            pending_event = json.loads(pending.read_text(encoding="utf-8"))
            self.assertEqual(pending_event["event_type"], "IMPORT_REVIEWED")

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stdout)

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

    def test_invalid_advanced_artifacts_are_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--advanced", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            manifest = Path(temp_dir) / "pgsa" / "skills" / "signed_skill_manifest.yaml"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["skills"][0]["risk"] = "extreme"
            data["skills"][0]["applies_to"] = ["unknown_session"]
            manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            evidence = Path(temp_dir) / "pgsa" / "evidence" / "runtime_evidence.jsonl"
            event = {
                "event_id": "runtime_evt_bad",
                "timestamp": "pending",
                "session": "backend",
                "event_type": "badtype",
                "status": "maybe",
                "evidence_ref": "local-summary",
                "risk": "extreme",
                "resource": "../secret",
            }
            evidence.write_text(json.dumps(event) + "\n", encoding="utf-8")

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            issues = json.loads(validate.stdout)["issues"]
            messages = "\n".join(issue["message"] for issue in issues)
            self.assertIn("skill risk should be one of", messages)
            self.assertIn("skill applies to unknown session", messages)
            self.assertIn("runtime evidence event_type should be namespaced", messages)
            self.assertIn("runtime evidence status should be one of", messages)
            self.assertIn("runtime evidence risk should be one of", messages)
            self.assertIn("runtime evidence resource should be a relative project artifact path", messages)

            strict = self.run_pgsa("--root", temp_dir, "validate", "--strict-advanced")
            self.assertEqual(strict.returncode, 1, strict.stdout)
            strict_issues = json.loads(strict.stdout)["issues"]
            self.assertTrue(
                any(issue["category"] == "advanced_capability_state" and issue["severity"] == "error" for issue in strict_issues)
            )

    def test_duplicate_ids_cycles_and_cognitive_audit_frontmatter_are_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--advanced", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            factory = Path(temp_dir) / "pgsa" / "factory" / "factory_plan.yaml"
            data = json.loads(factory.read_text(encoding="utf-8"))
            data["tasks"] = [
                {
                    "task_id": "task_a",
                    "session": "backend",
                    "depends_on": ["task_b"],
                    "outputs": ["state/backend.summary.md"],
                    "required_evidence": ["unit_tests"],
                },
                {
                    "task_id": "task_b",
                    "session": "frontend_components",
                    "depends_on": ["task_a"],
                    "outputs": ["state/frontend_components.summary.md"],
                    "required_evidence": ["consumer_review"],
                },
                {
                    "task_id": "task_c",
                    "session": "docs_security_integration",
                    "depends_on": [],
                    "outputs": ["state/docs_security_integration.summary.md"],
                    "required_evidence": ["review"],
                },
                {
                    "task_id": "task_c",
                    "session": "docs_security_integration",
                    "depends_on": [],
                    "outputs": ["state/docs_security_integration.summary.md"],
                    "required_evidence": ["review"],
                },
            ]
            factory.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            audit = Path(temp_dir) / "pgsa" / "audits" / "cognitive_audit_note.md"
            audit.write_text("# Missing frontmatter\n", encoding="utf-8")

            validate = self.run_pgsa("--root", temp_dir, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            messages = "\n".join(issue["message"] for issue in json.loads(validate.stdout)["issues"])
            self.assertIn("duplicate factory task_id: task_c", messages)
            self.assertIn("factory task graph contains a dependency cycle", messages)
            self.assertIn("cognitive audit note missing YAML frontmatter", messages)

    def test_advanced_schemas_define_typed_contracts(self) -> None:
        schema_names = [
            "verification_blueprint",
            "review_router",
            "session_runtime_profile",
            "capability_contract",
            "signed_skill_manifest",
            "factory_plan",
            "scenario_test",
            "runtime_evidence_event",
        ]
        for name in schema_names:
            path = REPO_ROOT / "protocol" / "schemas" / f"{name}.schema.json"
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object", name)
            self.assertTrue(schema.get("required"), name)
            self.assertTrue(schema.get("properties"), name)
            typed = [
                field
                for field in schema["properties"].values()
                if "type" in field or "enum" in field or "pattern" in field or "items" in field
            ]
            self.assertGreaterEqual(len(typed), 2, name)

    def test_advanced_init_artifacts_match_shipped_schema_subset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init = self.run_pgsa("--root", temp_dir, "init", "--advanced", "--force")
            self.assertEqual(init.returncode, 0, init.stderr)

            schema_to_artifact = {
                "verification_blueprint": "pgsa/gates/verification_blueprint.yaml",
                "review_router": "pgsa/gates/review_router.yaml",
                "session_runtime_profile": "pgsa/runtime/session_runtime_profile.yaml",
                "capability_contract": "pgsa/runtime/capability_contract.yaml",
                "signed_skill_manifest": "pgsa/skills/signed_skill_manifest.yaml",
                "factory_plan": "pgsa/factory/factory_plan.yaml",
                "scenario_test": "pgsa/scenarios/project.acceptance.v1.yaml",
            }
            for schema_name, artifact_rel in schema_to_artifact.items():
                schema = json.loads(
                    (REPO_ROOT / "protocol" / "schemas" / f"{schema_name}.schema.json").read_text(
                        encoding="utf-8"
                    )
                )
                artifact = json.loads((Path(temp_dir) / artifact_rel).read_text(encoding="utf-8"))
                _assert_schema_subset(artifact, schema, schema_name)

            evidence_schema = json.loads(
                (REPO_ROOT / "protocol" / "schemas" / "runtime_evidence_event.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence_path = Path(temp_dir) / "pgsa" / "evidence" / "runtime_evidence.jsonl"
            for line in evidence_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    _assert_schema_subset(json.loads(line), evidence_schema, "runtime_evidence_event")

            audit_schema = json.loads(
                (REPO_ROOT / "protocol" / "schemas" / "cognitive_audit_note.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            audit_frontmatter = _frontmatter(
                (Path(temp_dir) / "pgsa" / "audits" / "cognitive_audit_note.md").read_text(
                    encoding="utf-8"
                )
            )
            _assert_schema_subset(audit_frontmatter, audit_schema, "cognitive_audit_note")

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
