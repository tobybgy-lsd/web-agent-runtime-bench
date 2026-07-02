import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResolutionValidationRunnerTests(unittest.TestCase):
    def test_resolution_validation_runner_outputs_metrics(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_resolution_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((ROOT / "validation" / "resolution_validation_12.json").read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["total_cases"], 12)
        self.assertGreaterEqual(data["summary"]["correct_status"], 10)
        self.assertEqual(data["summary"]["forbidden_output_count"], 0)


if __name__ == "__main__":
    unittest.main()

