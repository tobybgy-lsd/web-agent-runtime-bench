import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OpenSourceEntryTests(unittest.TestCase):
    def test_readme_top_is_plain_product_entry(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        opening = readme[:1400]
        normalized_opening = " ".join(opening.split())

        for phrase in (
            "# Agent Failure Doctor",
            "Local-first failure diagnosis lifecycle tool for AI browser automation, Playwright, crawler, RPA, and business automation failures.",
            "trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt",
            "diagnosis, evidence, next action, repair suggestions, GitHub issue draft, Codex fix prompt.",
            "git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git",
            "cd web-agent-runtime-bench",
            "python -m pip install -e .",
            "failure-doctor diagnose .\\examples\\failed_runs\\proxy_network_error --out .\\report",
            "failure-doctor plan .\\report --out .\\fix_plan",
        ):
            self.assertIn(" ".join(phrase.split()), normalized_opening)

    def test_proxy_failed_example_matches_readme_command(self):
        pack = ROOT / "examples" / "failed_runs" / "proxy_failed"

        self.assertTrue((pack / "error.log").exists())
        self.assertTrue((pack / "README.txt").exists())

    def test_failure_case_issue_template_collects_sanitized_case_fields(self):
        template = ROOT / ".github" / "ISSUE_TEMPLATE" / "failure_case.yml"
        text = template.read_text(encoding="utf-8")

        for phrase in (
            "name: Submit a sanitized failure case",
            "What failed?",
            "Tool",
            "Playwright / browser-use / Scrapy / requests / Codex / RPA / other",
            "Input type",
            "trace.zip / error.log / console.txt / network.json / screenshot / description",
            "Expected result",
            "Actual result",
            "Sanitized error excerpt",
            "Can this become a public test case?",
        ):
            self.assertIn(phrase, text)

    def test_contributing_invites_sanitized_failure_cases_without_code(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        for phrase in (
            "You do not need to write code.",
            "The most useful contribution is a sanitized failure case.",
            "credentials",
            "cookies",
            "tokens",
            "whether this can become a public test case",
        ):
            self.assertIn(phrase, text)

    def test_community_post_drafts_request_failure_samples_not_stars(self):
        text = (ROOT / "docs" / "internal" / "COMMUNITY_POST_DRAFTS.md").read_text(encoding="utf-8")

        for phrase in (
            "I built a local-first failure doctor for AI browser automation, Playwright, and browser workflow debugging",
            "Please share sanitized failure logs, trace.zip files, or error descriptions",
            "Do not include secrets, cookies, tokens, credentials, or private user data.",
            "V2EX",
            "Juejin",
            "Reddit",
            "Hacker News Show HN",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
