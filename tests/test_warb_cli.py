import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent


class WarbCliTests(unittest.TestCase):
    def test_template_list_prints_builtin_failure_pack_templates(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "warb.py"),
                "template",
                "list",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("playwright_selector_drift_product_card", result.stdout)
        self.assertIn("playwright_auth_expired_login_page", result.stdout)
        self.assertIn("scrapy_rate_limit_soft_block", result.stdout)

    def test_template_copy_creates_editable_pack_from_builtin_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "copied_pack"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "warb.py"),
                    "template",
                    "copy",
                    "playwright_selector_drift_product_card",
                    "--out",
                    str(out_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((out_dir / "failure_artifact.json").exists())
            self.assertTrue((out_dir / "snapshot.html").exists())
            self.assertIn("Template copied", result.stdout)

            validate_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "warb.py"),
                    "validate",
                    str(out_dir / "failure_artifact.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stdout + validate_result.stderr)

    def test_template_copy_refuses_to_overwrite_existing_directory_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "copied_pack"
            out_dir.mkdir()
            (out_dir / "keep.txt").write_text("do not overwrite", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "warb.py"),
                    "template",
                    "copy",
                    "scrapy_rate_limit_soft_block",
                    "--out",
                    str(out_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("already exists", result.stdout + result.stderr)
            self.assertEqual((out_dir / "keep.txt").read_text(encoding="utf-8"), "do not overwrite")

    def test_adapt_playwright_trace_fixture_writes_diagnosable_artifact(self):
        fixture_dir = ROOT / "examples" / "playwright_trace_cli"
        trace_source = fixture_dir / "trace.trace"
        html_source = fixture_dir / "page.html"
        self.assertTrue(trace_source.exists(), "synthetic trace source fixture is missing")
        self.assertTrue(html_source.exists(), "synthetic HTML source fixture is missing")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            trace_zip = tmp_path / "trace.zip"
            out_dir = tmp_path / "out"
            with ZipFile(trace_zip, "w") as archive:
                archive.write(trace_source, "trace.trace")
                archive.write(html_source, "resources/page.html")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "warb.py"),
                    "adapt",
                    "playwright-trace",
                    str(trace_zip),
                    "--out",
                    str(out_dir),
                    "--run-id",
                    "pw_cli_fixture",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            artifact_path = out_dir / "failure_artifact.json"
            self.assertTrue(artifact_path.exists())
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

            self.assertEqual(artifact["run_id"], "pw_cli_fixture")
            self.assertEqual(artifact["tool"], "playwright")
            self.assertEqual(artifact["error"]["status_code"], 200)
            self.assertEqual(artifact["labels"]["failure_type"], "selector_drift")
            self.assertGreaterEqual(artifact["labels"]["confidence"], 0.7)
            self.assertEqual(artifact["observations"]["url"], "https://example.test/products")
            self.assertEqual(artifact["observations"]["failed_action"]["api_name"], "locator.waitFor")
            self.assertEqual(artifact["observations"]["failed_action"]["after_snapshot"], "after@7")
            self.assertEqual(artifact["observations"]["snapshot_refs"][0]["name"], "after@7")
            self.assertEqual(artifact["observations"]["snapshot_excerpts"][0]["name"], "after@7")
            self.assertIn(".amount", artifact["observations"]["dom_hints"]["candidate_selectors"])
            self.assertEqual(
                artifact["observations"]["network_events"],
                [{"method": "GET", "url": "https://example.test/products", "status": 200}],
            )
            self.assertIn("Timeout 30000ms waiting for selector .price", artifact["error"]["message"])
            self.assertIn("class='title'", artifact["observations"]["html_excerpt"])
            self.assertTrue(artifact["safety"]["sanitized"])
            self.assertFalse(artifact["safety"]["contains_credentials"])
            self.assertFalse(artifact["safety"]["external_network_required"])

    def test_adapt_smoke_script_generates_repair_outputs(self):
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "adapt_smoke_test.ps1"),
                "-Python",
                sys.executable,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ADAPTER SMOKE TEST: PASS", result.stdout)
        diagnosis_dir = ROOT / "outputs" / "adapt_playwright_trace" / "diagnosis"
        expected_files = [
            diagnosis_dir / "diagnosis.json",
            diagnosis_dir / "diagnosis.md",
            diagnosis_dir / "diagnosis_report.html",
            diagnosis_dir / "repair_prompt.md",
        ]
        for path in expected_files:
            self.assertTrue(path.exists(), f"{path} missing")

        diagnosis = json.loads((diagnosis_dir / "diagnosis.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnosis["failure_type"], "selector_drift")
        self.assertIn("selector", (diagnosis_dir / "repair_prompt.md").read_text(encoding="utf-8").lower())

    def test_adapt_diagnose_option_writes_repair_outputs(self):
        fixture_dir = ROOT / "examples" / "playwright_trace_cli"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            trace_zip = tmp_path / "trace.zip"
            out_dir = tmp_path / "out"
            with ZipFile(trace_zip, "w") as archive:
                archive.write(fixture_dir / "trace.trace", "trace.trace")
                archive.write(fixture_dir / "page.html", "resources/page.html")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "warb.py"),
                    "adapt",
                    "playwright-trace",
                    str(trace_zip),
                    "--out",
                    str(out_dir),
                    "--run-id",
                    "pw_cli_diagnose",
                    "--diagnose",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Initial diagnosis: selector_drift", result.stdout)
            self.assertIn("diagnosis.json", result.stdout)
            artifact_path = out_dir / "failure_artifact.json"
            diagnosis_dir = out_dir / "diagnosis"
            self.assertTrue(artifact_path.exists())
            for name in ("diagnosis.json", "diagnosis.md", "diagnosis_report.html", "repair_prompt.md"):
                self.assertTrue((diagnosis_dir / name).exists(), f"{name} missing")

            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
            diagnosis = json.loads((diagnosis_dir / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(artifact["labels"]["failure_type"], "selector_drift")
            self.assertEqual(diagnosis["failure_type"], "selector_drift")


if __name__ == "__main__":
    unittest.main()
