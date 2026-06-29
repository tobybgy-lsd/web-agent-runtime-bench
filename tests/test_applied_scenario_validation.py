import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "applied_scenarios"
VALIDATION = ROOT / "validation" / "applied_scenario_validation.json"


EXPECTED_SCENARIOS = {
    "01_hot_product_collector",
    "02_live_commerce_monitor",
    "03_ecommerce_listing_automation",
    "04_content_publishing_workflow",
    "05_gui_data_bridge",
    "06_erp_ecommerce_sync",
}


class AppliedScenarioValidationTests(unittest.TestCase):
    def test_applied_scenarios_have_required_structure(self):
        self.assertTrue(SCENARIOS.exists())
        self.assertEqual({path.name for path in SCENARIOS.iterdir() if path.is_dir()}, EXPECTED_SCENARIOS)

        total_cases = 0
        for scenario in sorted(EXPECTED_SCENARIOS):
            scenario_dir = SCENARIOS / scenario
            for required in [
                "README.md",
                "failed_run",
                "rerun_after_fix",
                "expected_diagnosis.json",
                "expected_fix_plan.json",
                "expected_verification.json",
                "regression_case.json",
                "cases",
            ]:
                self.assertTrue((scenario_dir / required).exists(), f"{scenario}/{required}")

            case_dirs = sorted(path for path in (scenario_dir / "cases").iterdir() if path.is_dir())
            self.assertGreaterEqual(len(case_dirs), 3, scenario)
            total_cases += len(case_dirs)
            for case_dir in case_dirs:
                for required in [
                    "README.md",
                    "failed_run",
                    "rerun_after_fix",
                    "expected_diagnosis.json",
                    "expected_fix_plan.json",
                    "expected_verification.json",
                    "regression_case.json",
                ]:
                    self.assertTrue((case_dir / required).exists(), f"{scenario}/{case_dir.name}/{required}")

        self.assertGreaterEqual(total_cases, 18)

    def test_runner_generates_applied_scenario_validation(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_applied_scenario_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(VALIDATION.read_text(encoding="utf-8"))
        self.assertEqual(summary["version"], "v1.1")
        self.assertEqual(summary["total_scenarios"], 6)
        self.assertGreaterEqual(summary["total_cases"], 18)
        self.assertGreaterEqual(summary["diagnosis_reasonable"], 16)
        self.assertGreaterEqual(summary["fix_plan_valid"], 18)
        self.assertGreaterEqual(summary["verification_correct"], 16)
        self.assertEqual(summary["forbidden_output_count"], 0)

    def test_version_and_docs_expose_current_package_and_v1_1_pack(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn('version = "2.1.0"', pyproject)
        self.assertIn("Applied Scenario Demos", readme)
        self.assertIn("run_applied_scenario_validation", readme)
        self.assertIn("## v1.1.0", changelog)


if __name__ == "__main__":
    unittest.main()
