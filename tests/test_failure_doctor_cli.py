import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FailureDoctorCliTests(unittest.TestCase):
    def test_failure_doctor_diagnoses_directory_inputs_and_writes_codex_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            out_dir = root / "report"
            input_dir.mkdir()
            (input_dir / "error.log").write_text(
                "TimeoutError: locator.click: Timeout waiting for selector button.submit\n"
                "Target page stayed on /checkout while modal overlay was visible\n",
                encoding="utf-8",
            )
            (input_dir / "network.json").write_text(
                json.dumps({"url": "https://example.test/api/checkout", "status": 200}),
                encoding="utf-8",
            )
            (input_dir / "user_description.txt").write_text(
                "AI agent failed when clicking the submit button. The page seemed loaded but the click never worked.",
                encoding="utf-8",
            )
            (input_dir / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("按钮/元素找不到", result.stdout)

            expected_files = {
                "diagnosis.json",
                "diagnosis.md",
                "evidence.json",
                "input_summary.json",
                "repair_suggestions.md",
                "issue_draft.md",
                "codex_fix_prompt.md",
                "failure_doctor_report.zip",
            }
            self.assertEqual(expected_files, {path.name for path in out_dir.iterdir() if path.is_file()})

            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            codex_prompt = (out_dir / "codex_fix_prompt.md").read_text(encoding="utf-8")

            self.assertEqual(diagnosis["user_facing_category"], "按钮/元素找不到")
            self.assertEqual(diagnosis["technical_category"], "selector_drift")
            self.assertEqual(diagnosis["next_action"], "把 codex_fix_prompt.md 交给 Codex/Claude 修改代码")
            self.assertIn(diagnosis["estimated_fix_difficulty"], {"easy", "medium", "hard"})
            self.assertTrue(diagnosis["confidence_reason"])
            self.assertIn("screenshot.png", evidence["inputs"]["screenshot_metadata"][0]["name"])
            self.assertIn("请修复这个 AI 自动化失败", codex_prompt)
            self.assertIn("不要改业务逻辑", codex_prompt)

            with zipfile.ZipFile(out_dir / "failure_doctor_report.zip") as archive:
                names = set(archive.namelist())
            self.assertIn("codex_fix_prompt.md", names)
            self.assertIn("diagnosis.json", names)

    def test_failure_doctor_reuses_trace_doctor_core_for_trace_zip(self):
        fixture_dir = ROOT / "examples" / "playwright_trace_cli"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_zip = root / "trace.zip"
            with zipfile.ZipFile(trace_zip, "w") as archive:
                archive.write(fixture_dir / "trace.trace", "trace.trace")
                archive.write(fixture_dir / "page.html", "resources/page.html")
            out_dir = root / "report"

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(trace_zip), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))

            self.assertEqual(diagnosis["technical_category"], "selector_drift")
            self.assertEqual(diagnosis["user_facing_category"], "按钮/元素找不到")
            self.assertEqual(evidence["inputs"]["trace_zip"], str(trace_zip))

    def test_failure_doctor_log_rules_detect_proxy_network_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "error.log"
            out_dir = root / "report"
            log.write_text(
                "Error: net::ERR_PROXY_CONNECTION_FAILED while opening https://example.test\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(log), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))

            self.assertEqual(diagnosis["user_facing_category"], "网络/代理问题")
            self.assertEqual(diagnosis["technical_category"], "network_http_error")
            self.assertEqual(diagnosis["subtype"], "proxy_connection_failed")


if __name__ == "__main__":
    unittest.main()
