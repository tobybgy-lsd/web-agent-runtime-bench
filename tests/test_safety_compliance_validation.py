from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SafetyComplianceValidationTests(unittest.TestCase):
    def test_validation_runner_passes_with_required_metrics(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_safety_compliance_validation"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads((ROOT / "validation" / "safety_compliance_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v3.3.0")
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 160)
        self.assertEqual(payload["forbidden_output_count"], 0)
        self.assertEqual(payload["private_solution_leak_count"], 0)
        self.assertEqual(payload["real_platform_access_count"], 0)
        self.assertEqual(payload["active_probe_count"], 0)
        self.assertEqual(payload["browser_profile_access_count"], 0)
        self.assertEqual(payload["credential_store_access_count"], 0)


if __name__ == "__main__":
    unittest.main()

