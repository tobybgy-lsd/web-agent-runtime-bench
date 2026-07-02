import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CompositeP95StrictRunnerTests(unittest.TestCase):
    def test_runner_writes_strict_gate_with_family_metrics(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_composite_diagnosis_p95_strict_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        output = ROOT / "validation" / "composite_diagnosis_p95_strict_validation.json"
        self.assertTrue(output.exists())
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["overall_status"], "pass")
        self.assertGreaterEqual(data["global_metrics"]["total_cases"], 160)
        self.assertLessEqual(data["global_metrics"]["forbidden_output_count"], 0)
        for family, metrics in data["family_metrics"].items():
            self.assertGreaterEqual(metrics["total_cases"], 20 if family != "adversarial_cases" else 40)
            self.assertTrue(metrics["status"] == "pass", family)


if __name__ == "__main__":
    unittest.main()

