import json
import unittest
from pathlib import Path

from tools.validation.run_enterprise_governance_validation import main as run_validation


class EnterpriseGovernanceValidationTests(unittest.TestCase):
    def test_enterprise_validation_runner_passes(self):
        result = run_validation()
        self.assertEqual(result["version"], "v4.1.0")
        self.assertEqual(result["status"], "pass")
        self.assertGreaterEqual(result["total_cases"], 180)
        self.assertEqual(result["unauthorized_action_blocked"], 180)
        self.assertEqual(result["external_api_call_count"], 0)
        self.assertEqual(result["telemetry_call_count"], 0)
        self.assertEqual(result["private_solution_in_workspace"], 0)
        self.assertEqual(result["forbidden_output_count"], 0)
        saved = json.loads(Path("validation/enterprise_governance_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "pass")


if __name__ == "__main__":
    unittest.main()


