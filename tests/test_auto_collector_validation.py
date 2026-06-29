import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutoCollectorValidationTests(unittest.TestCase):
    def test_validation_runner_writes_passing_metrics(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_auto_collector_validation"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((ROOT / "validation" / "auto_collector_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 90)
        self.assertGreaterEqual(payload["collection_success"], 88)
        self.assertEqual(payload["out_of_scope_files_collected"], 0)
        self.assertEqual(payload["raw_secret_in_sanitized_output"], 0)
        self.assertEqual(payload["forbidden_output_count"], 0)

