import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExternalValidationPackTests(unittest.TestCase):
    def test_external_failure_case_template_exists_and_collects_consent(self):
        template = ROOT / ".github" / "ISSUE_TEMPLATE" / "external_failure_case.yml"
        self.assertTrue(template.exists())
        text = template.read_text(encoding="utf-8")

        for phrase in (
            "name: External failure case",
            "external-failure-case",
            "needs-triage",
            "Tool",
            "Input type",
            "What failed",
            "Expected behavior",
            "Actual behavior",
            "Sanitized error excerpt",
            "Can this become a public validation case?",
            "I confirm no credentials/cookies/tokens/private data are included.",
        ):
            self.assertIn(phrase, text)

    def test_external_validation_contract_files_exist(self):
        for rel in (
            "schemas/external_failure_case.schema.json",
            "validation/external_cases/README.md",
            "validation/external_reports/.gitkeep",
            "validation/external_validation_dashboard.md",
            "docs/external_validation_protocol.md",
            "docs/REAL_TRACE_CONTRIBUTION_GUIDE.md",
            "examples/external_case_template/README.md",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_external_case_schema_tracks_first_run_evidence(self):
        schema = json.loads((ROOT / "schemas" / "external_failure_case.schema.json").read_text(encoding="utf-8"))
        required = set(schema["required"])
        for field in (
            "case_id",
            "source",
            "source_url",
            "submitted_by_external_user",
            "input_type",
            "tool",
            "sanitized",
            "permission_to_add_to_public_corpus",
            "first_run_version",
            "first_run_commit",
            "expected_category_by_maintainer",
            "actual_category_first_run",
            "actual_subtype_first_run",
            "result",
            "actionable_next_action",
            "forbidden_output",
            "became_regression_test",
        ):
            self.assertIn(field, required)

    def test_external_dashboard_starts_at_zero_without_fake_cases(self):
        dashboard = (ROOT / "validation" / "external_validation_dashboard.md").read_text(encoding="utf-8")
        for phrase in (
            "| External failure issues received | 0 |",
            "| Accepted sanitized cases | 0 |",
            "| Unique external submitters | 0 |",
            "| First-run reasonable classification | N/A |",
            "| Actionable next_action | N/A |",
            "| Severe misclassification | 0 |",
            "| Forbidden output | 0 |",
            "| Regression tests added | 0 |",
            "No external cases have been accepted yet.",
        ):
            self.assertIn(phrase, dashboard)

    def test_external_runner_handles_zero_cases_and_writes_results(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_external_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((ROOT / "validation" / "external_validation_results.json").read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["external_cases_total"], 0)
        self.assertEqual(data["summary"]["accepted_sanitized_cases"], 0)
        self.assertEqual(data["summary"]["forbidden_output"], 0)
        self.assertEqual(data["cases"], [])

    def test_docs_explain_no_sensitive_data_for_external_cases(self):
        combined = "\n".join(
            (ROOT / rel).read_text(encoding="utf-8")
            for rel in ("SECURITY.md", "CONTRIBUTING.md", "README.md", "README.zh-CN.md")
        )
        for phrase in (
            "cookies",
            "tokens",
            "credentials",
            "private data",
        ):
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()

