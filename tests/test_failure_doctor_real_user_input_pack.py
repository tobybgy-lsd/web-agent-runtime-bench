import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from failure_doctor.cli import collect_inputs, input_summary_for


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "failed_runs"


class FailureDoctorRealUserInputPackTests(unittest.TestCase):
    def test_writes_input_summary_json_for_mixed_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "my_failed_run"
            out_dir = root / "report"
            input_dir.mkdir()
            (input_dir / "error.log").write_text("page.goto: net::ERR_PROXY_CONNECTION_FAILED", encoding="utf-8")
            (input_dir / "console.txt").write_text("console warning before failure", encoding="utf-8")
            (input_dir / "network.json").write_text(json.dumps({"url": "https://example.test", "status": 503}), encoding="utf-8")
            (input_dir / "README.txt").write_text("User says the automation failed during checkout.", encoding="utf-8")
            (input_dir / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads((out_dir / "input_summary.json").read_text(encoding="utf-8"))

            self.assertEqual(summary["source"], str(input_dir))
            self.assertEqual(summary["observed_evidence"]["logs"], 2)
            self.assertEqual(summary["observed_evidence"]["network_events"], 1)
            self.assertEqual(summary["observed_evidence"]["screenshots"], 1)
            self.assertIn("trace_zip", summary["missing_evidence"])

    def test_diagnosis_json_includes_missing_evidence_and_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "error.log"
            out_dir = root / "report"
            log.write_text("Error: page.goto: net::ERR_NAME_NOT_RESOLVED", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(log), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))

            self.assertEqual(diagnosis["evidence_priority"], ["log"])
            self.assertIn("trace_zip", diagnosis["missing_evidence"])
            self.assertIn("network.json", diagnosis["missing_evidence"])

    def test_evidence_priority_prefers_trace_over_logs_network_description_and_screenshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "mixed"
            input_dir.mkdir()
            fixture_dir = ROOT / "examples" / "playwright_trace_cli"
            with zipfile.ZipFile(input_dir / "trace.zip", "w") as archive:
                archive.write(fixture_dir / "trace.trace", "trace.trace")
                archive.write(fixture_dir / "page.html", "resources/page.html")
            (input_dir / "error.log").write_text("page.goto: net::ERR_PROXY_CONNECTION_FAILED", encoding="utf-8")
            (input_dir / "network.json").write_text(json.dumps({"status": 503}), encoding="utf-8")
            (input_dir / "user_description.txt").write_text("network failed", encoding="utf-8")
            (input_dir / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")

            evidence = collect_inputs(input_dir)
            summary = input_summary_for(evidence)

            self.assertEqual(summary["evidence_priority"], ["trace_zip", "log", "network", "description", "screenshot_metadata"])

    def test_low_evidence_screenshot_only_downgrades_to_insufficient_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            out_dir = root / "report"
            input_dir.mkdir()
            (input_dir / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
            report = (out_dir / "diagnosis.md").read_text(encoding="utf-8")

            self.assertEqual(diagnosis["technical_category"], "insufficient_evidence")
            self.assertEqual(diagnosis["evidence_level"], "low")
            self.assertIn("需要补充", report)
            self.assertIn("error.log", diagnosis["missing_evidence"])

    def test_readme_txt_is_treated_as_user_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.txt").write_text("The agent failed after clicking export.", encoding="utf-8")

            evidence = collect_inputs(root)
            summary = input_summary_for(evidence)

            self.assertEqual(summary["observed_evidence"]["descriptions"], 1)
            self.assertEqual(summary["evidence_priority"], ["description"])

    def test_description_only_downgrades_to_insufficient_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            out_dir = root / "report"
            input_dir.mkdir()
            (input_dir / "README.txt").write_text("The AI automation failed, but no logs are available.", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))

            self.assertEqual(diagnosis["technical_category"], "insufficient_evidence")
            self.assertEqual(diagnosis["evidence_priority"], ["description"])

    def test_report_zip_includes_input_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "error.log"
            out_dir = root / "report"
            log.write_text("locator.click: Error: strict mode violation: locator('button') resolved to 2 elements", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(log), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(out_dir / "failure_doctor_report.zip") as archive:
                self.assertIn("input_summary.json", set(archive.namelist()))

    def test_examples_failed_runs_contains_five_runnable_packs(self):
        packs = [path for path in EXAMPLES.iterdir() if path.is_dir()]
        self.assertEqual(len(packs), 5)
        for pack in packs:
            self.assertTrue(any(item.name in {"error.log", "console.txt", "network.json", "README.txt", "user_description.txt", "screenshot.png", "trace.zip"} for item in pack.iterdir()), pack)

    def test_each_example_failed_run_can_generate_report(self):
        for pack in sorted(path for path in EXAMPLES.iterdir() if path.is_dir()):
            with tempfile.TemporaryDirectory() as tmp:
                out_dir = Path(tmp) / "report"
                result = subprocess.run(
                    [sys.executable, "-m", "failure_doctor", "diagnose", str(pack), "--out", str(out_dir)],
                    cwd=ROOT,
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                )

                self.assertEqual(result.returncode, 0, pack.name + result.stdout + result.stderr)
                self.assertTrue((out_dir / "input_summary.json").exists(), pack.name)
                self.assertTrue((out_dir / "diagnosis.md").exists(), pack.name)

    def test_readme_has_one_minute_quickstart(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("一分钟上手", readme)
        self.assertIn("python -m failure_doctor diagnose .\\examples\\failed_runs", readme)


if __name__ == "__main__":
    unittest.main()
