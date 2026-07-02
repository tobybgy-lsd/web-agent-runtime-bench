import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseAlignmentPackTests(unittest.TestCase):
    def test_readme_first_screen_shows_current_lifecycle_commands(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        opening = readme[:2200]

        self.assertIn("Current milestone: Agent Failure Doctor v5.1 Android APK UI Automation Adapter Pack", opening)
        self.assertIn("Earlier stable line: Agent Failure Doctor v3.9.0", opening)
        self.assertIn("P98 gate:", opening)
        self.assertNotIn("Current milestone: v0.8", opening)
        for phrase in (
            "failure-doctor diagnose",
            "`diagnose` / `plan` / `verify` / `run`",
            "`sanitize` / `adapt`",
            "failure-doctor agent-bootstrap",
            "`failure-doctor propose-patch`",
            "`failure-doctor batch`",
            "diagnose -> plan -> AI handoff / patch proposal",
            "-> verify -> sanitize/share",
        ):
            self.assertIn(phrase, opening)

    def test_project_positioning_release_notes_and_faq_exist(self):
        positioning = ROOT / "docs" / "PROJECT_POSITIONING.md"
        release_notes = ROOT / "docs" / "RELEASE_NOTES_v2.1.0.md"
        faq = ROOT / "docs" / "FAQ.md"
        for path in (positioning, release_notes, faq):
            self.assertTrue(path.exists(), path)

        positioning_text = positioning.read_text(encoding="utf-8")
        for phrase in (
            "local-first failure lifecycle tool",
            "not a crawler execution framework",
            "not a CAPTCHA bypass tool",
            "not a bot evasion tool",
            "not an ecommerce system",
            "not an ERP system",
            "Local-first failure diagnosis, repair planning, fix verification, auto-capture, and sanitized sharing",
        ):
            self.assertIn(phrase, positioning_text)

        release_text = release_notes.read_text(encoding="utf-8")
        for phrase in (
            "Agent Failure Doctor v2.1.0",
            "Failure Resolution Loop",
            "Applied Scenario Demos",
            "Integration Adapters",
            "Validation Hardening",
            "Auto Capture",
            "Sanitize & Share",
            "Known limits",
        ):
            self.assertIn(phrase, release_text)

        faq_text = faq.read_text(encoding="utf-8")
        for question in (
            "Is this a crawler?",
            "Is this a CAPTCHA bypass tool?",
            "How is it different from Playwright Trace Viewer?",
            "Can it modify code automatically?",
            "How do I share a failure case safely?",
            "Which frameworks are deeply supported?",
            "What are the current limits?",
        ):
            self.assertIn(question, faq_text)

    def test_showcase_reports_exist_and_are_sanitized(self):
        showcase = ROOT / "sample_reports" / "showcase"
        expected = {
            "01_ecommerce_listing_failure",
            "02_real_trace_login_redirect",
            "03_sanitize_share_pack",
        }
        self.assertEqual({p.name for p in showcase.iterdir() if p.is_dir()}, expected)

        forbidden = (
            "Authorization:",
            "Cookie:",
            "Bearer ",
            "sk-",
            "sessionid=",
            "password=",
            "secret-token",
        )
        for case_dir in showcase.iterdir():
            if not case_dir.is_dir():
                continue
            for required in ("README.md", "diagnosis.md", "fix_plan.md", "codex_fix_prompt.md"):
                self.assertTrue((case_dir / required).exists(), f"{case_dir.name}/{required}")
            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in case_dir.rglob("*")
                if path.is_file() and path.suffix in {".md", ".json"}
            )
            for marker in forbidden:
                self.assertNotIn(marker, combined, f"{case_dir.name}: {marker}")
            redaction = case_dir / "redaction_report.json"
            if redaction.exists():
                payload = json.loads(redaction.read_text(encoding="utf-8"))
                self.assertIn("total_redactions", payload)

    def test_architecture_contains_release_alignment_flow(self):
        architecture = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
        for phrase in (
            "failure-doctor run",
            "failure pack",
            "diagnose",
            "plan",
            "verify",
            "sanitize/share",
            "regression case",
        ):
            self.assertIn(phrase, architecture)


if __name__ == "__main__":
    unittest.main()


