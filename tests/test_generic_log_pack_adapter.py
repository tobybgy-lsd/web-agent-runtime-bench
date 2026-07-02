import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GenericLogPackAdapterTests(unittest.TestCase):
    def test_pack_logs_normalizes_raw_folder_and_is_diagnosable(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw = tmp_path / "raw_logs"
            raw.mkdir()
            (raw / "failure.txt").write_text("Download event fired but file was not saved; acceptDownloads is false", encoding="utf-8")
            (raw / "console.txt").write_text("local console output", encoding="utf-8")
            (raw / "network.json").write_text(json.dumps([{"url": "https://local.mock/export", "status": 200}]), encoding="utf-8")
            (raw / "README.txt").write_text("User says the export automation failed after clicking download.", encoding="utf-8")
            (raw / "screenshot.png").write_bytes(b"fake-png")

            pack = tmp_path / "failure_pack"
            report = tmp_path / "report"
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "pack-logs", str(raw), "--out", str(pack)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((pack / "error.log").exists())
            summary = json.loads((pack / "input_summary.json").read_text(encoding="utf-8"))
            self.assertIn("log", summary["evidence_priority"])
            self.assertIn("trace_zip", summary["missing_evidence"])

            diagnose = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(pack), "--out", str(report)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(diagnose.returncode, 0, diagnose.stdout + diagnose.stderr)
            diagnosis = json.loads((report / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(diagnosis["technical_category"], "playwright_download")


if __name__ == "__main__":
    unittest.main()

