import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PlaywrightCollectorTests(unittest.TestCase):
    def test_collect_playwright_creates_diagnosable_failure_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            results = tmp_path / "test-results"
            case = results / "checkout-flow"
            case.mkdir(parents=True)
            with zipfile.ZipFile(case / "trace.zip", "w") as archive:
                archive.writestr(
                    "trace.trace",
                    json.dumps(
                        {
                            "type": "after",
                            "callId": "call@1",
                            "error": {"message": "Timeout waiting for selector .submit"},
                        }
                    )
                    + "\n",
                )
            (case / "error-context.md").write_text(
                "locator.click: Timeout waiting for selector .submit; old selector not found",
                encoding="utf-8",
            )
            (case / "screenshot.png").write_bytes(b"fake-png")
            (case / "network.json").write_text(json.dumps([{"url": "https://local.mock/checkout", "status": 200}]), encoding="utf-8")

            pack = tmp_path / "failure_pack"
            report = tmp_path / "report"
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "collect-playwright", str(results), "--out", str(pack)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for rel in ("trace.zip", "error.log", "network.json", "user_description.txt", "input_summary.json"):
                self.assertTrue((pack / rel).exists(), rel)

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
            self.assertIn("raw_diagnosis", diagnosis)


if __name__ == "__main__":
    unittest.main()
