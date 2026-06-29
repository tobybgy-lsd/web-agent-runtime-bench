import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PrivateSpiderbufBoundaryTests(unittest.TestCase):
    def test_private_spiderbuf_tools_are_not_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "tools/spiderbuf"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip(), "")

    def test_private_spiderbuf_path_is_gitignored(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("Private challenge workbench - never publish", gitignore)
        self.assertIn("tools/spiderbuf/", gitignore)

    def test_public_runtime_demo_does_not_give_bypass_steps(self):
        text = (ROOT / "demo" / "phase5_2_runtime" / "runtime_error_classifier.py").read_text(
            encoding="utf-8"
        )
        forbidden_phrases = (
            "ActionChains: click_and_hold",
            "move_by_offset + release",
            "--disable-blink-features=AutomationControlled",
            "Simulate random mouse movement",
            "Execute JS in browser context to decrypt data",
            "worker interception",
        )

        for phrase in forbidden_phrases:
            self.assertNotIn(phrase, text)

        self.assertIn("anti_bot_risk_boundary", text)
        self.assertIn("manual verification", text)
        self.assertIn("official API", text)

    def test_spiderbuf_inspired_sources_are_local_diagnosis_only(self):
        source_files = sorted((ROOT / "examples" / "spiderbuf_inspired_challenges").glob("*/source.json"))
        self.assertGreater(len(source_files), 0)

        for source_file in source_files:
            payload = json.loads(source_file.read_text(encoding="utf-8"))
            serialized = json.dumps(payload, ensure_ascii=False).lower()
            self.assertIn("local_only", serialized, source_file)
            self.assertIn("diagnosis_only_no_bypass", serialized, source_file)

    def test_public_expected_fix_plans_do_not_include_bypass_instructions(self):
        paths = list((ROOT / "examples" / "spiderbuf_inspired_challenges").glob("*/expected_fix_plan.json"))
        paths += list((ROOT / "examples" / "spiderbuf_inspired_challenges").glob("*/source.json"))
        forbidden = (
            "captcha bypass",
            "anti-bot evasion",
            "fingerprint spoofing",
            "signature cracking",
            "slider automation",
            "cloudflare bypass",
            "clearance",
            "click_and_hold",
            "move_by_offset",
        )

        for path in paths:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for phrase in forbidden:
                self.assertNotIn(phrase, text, f"{phrase!r} leaked in {path}")


if __name__ == "__main__":
    unittest.main()
