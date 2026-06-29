import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OpenSourceAdoptionPackTests(unittest.TestCase):
    def test_failure_case_issue_template_collects_consent_and_required_fields(self):
        text = (ROOT / ".github" / "ISSUE_TEMPLATE" / "failure_case.yml").read_text(encoding="utf-8")

        for phrase in (
            "name: Failure case report",
            'title: "[Failure Case]: "',
            "failure-case",
            "needs-triage",
            "python -m pip install agent-failure-doctor",
            "Framework / runtime",
            "Failure area",
            "What happened?",
            "Expected behavior",
            "Sanitized artifacts",
            "raw_local_only_do_not_share",
            "I confirm this report contains no credentials/cookies/tokens/private data.",
        ):
            self.assertIn(phrase, text)

    def test_pr_template_guides_safe_contributions(self):
        text = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

        for phrase in (
            "What changed?",
            "Is this a new failure case?",
            "Did you add tests?",
            "Did you run unit tests?",
            "Did you run safety scan?",
            "Does this include any sensitive data? no",
        ):
            self.assertIn(phrase, text)

    def test_docs_for_discussions_release_and_announcement_exist(self):
        for rel in (
            "docs/DISCUSSIONS_GUIDE.md",
            "docs/RELEASE_TEMPLATE.md",
            "docs/internal/ANNOUNCEMENT_DRAFT.md",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)

        discussions = (ROOT / "docs" / "DISCUSSIONS_GUIDE.md").read_text(encoding="utf-8")
        for phrase in ("Failure Cases", "Ideas", "Show and Tell"):
            self.assertIn(phrase, discussions)

        announcement = (ROOT / "docs" / "internal" / "ANNOUNCEMENT_DRAFT.md").read_text(encoding="utf-8")
        self.assertIn("I built a local-first failure doctor for AI browser automation, Playwright, and crawler debugging", announcement)
        self.assertIn("欢迎提交脱敏后的失败日志", announcement)
        self.assertIn("not asking for stars", announcement.lower())


if __name__ == "__main__":
    unittest.main()
