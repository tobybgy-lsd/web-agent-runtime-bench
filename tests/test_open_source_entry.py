import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OpenSourceEntryTests(unittest.TestCase):
    def test_readme_top_is_plain_product_entry(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        opening = readme[:900]

        for phrase in (
            "# Agent Failure Doctor",
            "Diagnose why AI-generated browser automation / crawler / RPA runs failed.",
            "trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt",
            "diagnosis, evidence, next action, repair suggestions, Codex fix prompt.",
            "git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git",
            "cd web-agent-runtime-bench",
            "python -m failure_doctor diagnose .\\examples\\failed_runs\\proxy_failed --out .\\report",
        ):
            self.assertIn(phrase, opening)

    def test_proxy_failed_example_matches_readme_command(self):
        pack = ROOT / "examples" / "failed_runs" / "proxy_failed"

        self.assertTrue((pack / "error.log").exists())
        self.assertTrue((pack / "README.txt").exists())

    def test_failure_case_issue_template_collects_sanitized_case_fields(self):
        template = ROOT / ".github" / "ISSUE_TEMPLATE" / "failure_case.yml"
        text = template.read_text(encoding="utf-8")

        for phrase in (
            "name: Failure case",
            "What failed?",
            "What tool?",
            "Playwright / browser-use / Codex / RPA / other",
            "Input type",
            "log / trace / network / screenshot / description",
            "Expected result",
            "Actual result",
            "Sanitized log",
            "Can this become a public test case?",
        ):
            self.assertIn(phrase, text)

    def test_contributing_invites_sanitized_failure_cases_without_code(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        for phrase in (
            "You do not need to write code.",
            "Submit a sanitized failure case",
            "Do not include passwords, API keys, cookies, tokens, authorization headers, or private screenshots.",
            "Can this become a public test case?",
        ):
            self.assertIn(phrase, text)

    def test_community_post_drafts_request_failure_samples_not_stars(self):
        text = (ROOT / "docs" / "COMMUNITY_POST_DRAFTS.md").read_text(encoding="utf-8")

        for phrase in (
            "I built a local-first failure doctor for AI browser automation, Playwright, and browser workflow debugging",
            "我做了一个本地优先的 AI 自动化失败诊断工具",
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
