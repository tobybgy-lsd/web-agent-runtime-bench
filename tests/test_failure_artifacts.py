import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.failure_artifacts.artifact import (
    discover_seed_artifacts,
    load_artifact,
    validate_artifact,
)
from tools.failure_artifacts.diagnose import diagnose_artifact
from tools.failure_artifacts.packager import package_failure_dir
from tools.failure_artifacts.report import render_markdown_report, write_report


ROOT = Path(__file__).resolve().parents[1]


class FailureArtifactTests(unittest.TestCase):
    def test_seed_corpus_has_ten_valid_sanitized_artifacts(self):
        seeds = discover_seed_artifacts(ROOT / "examples" / "failures")

        self.assertEqual(len(seeds), 10)
        for path in seeds:
            artifact = load_artifact(path)
            errors = validate_artifact(artifact, base_dir=path.parent)
            self.assertEqual(errors, [], msg=f"{path} failed validation: {errors}")
            self.assertTrue(artifact["safety"]["sanitized"])
            self.assertFalse(artifact["safety"]["contains_credentials"])

    def test_diagnose_seed_corpus_covers_five_priority_failure_types(self):
        expected = {
            "runtime_api_missing",
            "network_http_error",
            "response_shape_change",
            "auth_expiry",
            "captcha_or_bot_wall",
        }
        actual = set()
        for path in discover_seed_artifacts(ROOT / "examples" / "failures"):
            diagnosis = diagnose_artifact(load_artifact(path))
            if diagnosis["failure_type"] in expected:
                actual.add(diagnosis["failure_type"])
            self.assertGreaterEqual(diagnosis["confidence"], 0.65)
            self.assertTrue(diagnosis["evidence"])

        self.assertEqual(actual, expected)

    def test_report_renderer_includes_evidence_fix_and_safety(self):
        artifact_path = ROOT / "examples" / "failures" / "seed_004_auth_expiry" / "failure_artifact.json"
        artifact = load_artifact(artifact_path)
        diagnosis = diagnose_artifact(artifact)

        markdown = render_markdown_report(artifact, diagnosis)

        self.assertIn("# Failure Diagnosis Report", markdown)
        self.assertIn("auth_expiry", markdown)
        self.assertIn("Evidence", markdown)
        self.assertIn("Suggested Fix", markdown)
        self.assertIn("Sanitized: yes", markdown)

    def test_write_report_creates_markdown_file(self):
        artifact_path = ROOT / "examples" / "failures" / "seed_001_runtime_window_missing" / "failure_artifact.json"
        artifact = load_artifact(artifact_path)
        diagnosis = diagnose_artifact(artifact)

        with tempfile.TemporaryDirectory() as tmp:
            out = write_report(artifact, diagnosis, Path(tmp))

            self.assertTrue(out.exists())
            self.assertIn("runtime_api_missing", out.read_text(encoding="utf-8"))

    def test_package_failure_dir_sanitizes_files_and_generates_issue_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "raw"
            out = tmp_path / "pack"
            src.mkdir()
            (src / "error.log").write_text(
                "Authorization: Bearer secret-token-123\n"
                "Cookie: sessionid=private-cookie\n"
                "Timeout waiting for selector .price\n",
                encoding="utf-8",
            )
            (src / "snapshot.html").write_text(
                '<html><input type="password" value="hunter2"></html>',
                encoding="utf-8",
            )
            (src / "expected_schema.json").write_text('{"required": ["title", "price"]}', encoding="utf-8")
            (src / "actual_output.json").write_text('{"title": "demo"}', encoding="utf-8")

            result = package_failure_dir(
                src,
                out,
                tool="playwright",
                run_id="pack_001",
                summary="Product page returned a login form",
                required_fields=["title", "price"],
                status_code=200,
            )

            artifact_path = Path(result["artifact_path"])
            artifact = load_artifact(artifact_path)
            errors = validate_artifact(artifact, base_dir=artifact_path.parent)

            self.assertEqual(errors, [])
            self.assertTrue((out / "github_issue.md").exists())
            self.assertTrue((out / "failure_pack.zip").exists())
            self.assertIn("auth_expiry", result["diagnosis"]["failure_type"])
            self.assertNotIn("secret-token-123", (out / "error.log").read_text(encoding="utf-8"))
            self.assertNotIn("private-cookie", (out / "error.log").read_text(encoding="utf-8"))
            self.assertNotIn("hunter2", (out / "snapshot.html").read_text(encoding="utf-8"))
            self.assertIn("failure_artifact.json", ZipFile(out / "failure_pack.zip").namelist())


if __name__ == "__main__":
    unittest.main()
