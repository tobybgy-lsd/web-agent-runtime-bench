import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutoCaptureRunCliTests(unittest.TestCase):
    def test_run_command_captures_failed_process_and_generates_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace = tmp_path / ".failure-doctor"
            script = (
                "import sys; "
                "print('starting crawler'); "
                "print('Authorization: Bearer super-secret-token', file=sys.stderr); "
                "print('page.goto: net::ERR_PROXY_CONNECTION_FAILED at https://example.test', file=sys.stderr); "
                "sys.exit(7)"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "run",
                    "--workspace",
                    str(workspace),
                    "--run-id",
                    "case_proxy",
                    "--",
                    sys.executable,
                    "-c",
                    script,
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(result.returncode, 7, result.stdout + result.stderr)

            run_dir = workspace / "runs" / "case_proxy"
            self.assertTrue((run_dir / "command.txt").exists())
            self.assertEqual((run_dir / "exit_code.txt").read_text(encoding="utf-8").strip(), "7")
            self.assertIn("starting crawler", (run_dir / "stdout.log").read_text(encoding="utf-8"))
            stderr = (run_dir / "stderr.log").read_text(encoding="utf-8")
            self.assertIn("[REDACTED_BEARER_TOKEN]", stderr)
            self.assertNotIn("super-secret-token", stderr)

            for rel in (
                "environment.json",
                "detected_artifacts.json",
                "input_summary.json",
                "redaction_report.json",
                "safe_to_share.json",
                "verification_hint.md",
                "shareable_failure_pack.zip",
                "diagnosis/diagnosis.json",
                "fix_plan/fix_plan.json",
            ):
                self.assertTrue((run_dir / rel).exists(), rel)

            diagnosis = json.loads((run_dir / "diagnosis" / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(diagnosis["technical_category"], "network_http_error")
            safe = json.loads((run_dir / "safe_to_share.json").read_text(encoding="utf-8"))
            self.assertFalse(safe["safe_to_share"])
            self.assertIn("manual review", safe["reason"].lower())

            with zipfile.ZipFile(run_dir / "shareable_failure_pack.zip") as archive:
                names = set(archive.namelist())
            self.assertIn("stdout.log", names)
            self.assertIn("stderr.log", names)
            self.assertIn("diagnosis/diagnosis.json", names)

    def test_run_command_records_success_without_forcing_diagnosis(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / ".failure-doctor"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "run",
                    "--workspace",
                    str(workspace),
                    "--run-id",
                    "case_success",
                    "--",
                    sys.executable,
                    "-c",
                    "print('ok')",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_dir = workspace / "runs" / "case_success"
            self.assertEqual((run_dir / "exit_code.txt").read_text(encoding="utf-8").strip(), "0")
            self.assertTrue((run_dir / "stdout.log").exists())
            self.assertTrue((run_dir / "safe_to_share.json").exists())
            self.assertFalse((run_dir / "diagnosis").exists())

    def test_docs_and_version_expose_v2_auto_capture(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "2.4.1"', pyproject)
        self.assertIn("## v2.1.0", changelog)
        self.assertIn("## v2.0.0", changelog)
        self.assertIn("failure-doctor run --", readme)
        self.assertIn("Auto Capture", readme)


if __name__ == "__main__":
    unittest.main()

