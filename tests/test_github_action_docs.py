import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GitHubActionDocsTests(unittest.TestCase):
    def test_github_action_usage_exists_and_is_local_first(self):
        action = ROOT / ".github" / "actions" / "failure-doctor-diagnose" / "action.yml"
        docs = ROOT / "docs" / "GITHUB_ACTION_USAGE.md"
        self.assertTrue(action.exists())
        self.assertTrue(docs.exists())
        text = docs.read_text(encoding="utf-8")
        self.assertIn("failure-doctor diagnose", text)
        self.assertIn("local-first", text.lower())
        self.assertIn("upload-artifact", text)
        lowered = text.lower()
        for forbidden in ("captcha bypass", "bot evasion", "fingerprint spoofing", "bypass cloudflare"):
            self.assertNotIn(forbidden, lowered)

    def test_integrations_overview_links_all_adapters(self):
        text = (ROOT / "docs" / "INTEGRATIONS.md").read_text(encoding="utf-8")
        for phrase in (
            "collect-playwright",
            "pack-logs",
            "browser-use",
            "GitHub Actions",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

