import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class IssueTemplateDistributionTests(unittest.TestCase):
    def test_failure_case_template_guides_sanitized_pypi_reports(self):
        template = ROOT / ".github" / "ISSUE_TEMPLATE" / "failure_case.yml"

        self.assertTrue(template.exists(), "failure_case.yml should exist")
        text = template.read_text(encoding="utf-8")

        self.assertIn("python -m pip install agent-failure-doctor", text)
        self.assertIn("sanitize", text.lower())
        self.assertIn("raw_local_only_do_not_share", text)
        for phrase in [
            "CAPTCHA bypass",
            "anti-bot evasion",
            "fingerprint spoofing",
            "signature cracking",
        ]:
            self.assertIn(phrase, text)

    def test_distribution_issue_forms_are_present(self):
        issue_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
        for name in [
            "config.yml",
            "failure_case.yml",
            "bug_report.yml",
            "feature_request.yml",
            "safety_boundary.yml",
        ]:
            self.assertTrue((issue_dir / name).exists(), f"{name} should exist")

    def test_release_notes_and_about_docs_include_pypi_install(self):
        release_notes = (ROOT / "docs" / "RELEASE_NOTES_v3.9.0.md").read_text(
            encoding="utf-8"
        )
        about_doc = ROOT / "docs" / "manual_update_github_about.md"

        self.assertIn("python -m pip install agent-failure-doctor", release_notes)
        self.assertIn("https://pypi.org/project/agent-failure-doctor/", release_notes)
        self.assertTrue(about_doc.exists(), "manual_update_github_about.md should exist")
        self.assertIn(
            "Local-first failure diagnosis",
            about_doc.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
