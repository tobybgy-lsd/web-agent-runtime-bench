import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseNotesPresenceTests(unittest.TestCase):
    def test_release_notes_exist_for_public_alignment_milestones(self):
        versions = (
            "v2.4.1",
            "v2.5.0",
            "v2.6.0",
            "v3.0.0",
            "v3.0.1",
            "v3.2.2",
            "v3.2.3",
            "v3.2.4",
            "v3.2.5",
            "v3.2.6",
            "v3.2.7",
            "v3.2.8",
            "v3.3.0",
            "v4.0.0",
            "v5.1.0",
        )

        for version in versions:
            with self.subTest(version=version):
                path = ROOT / "docs" / f"RELEASE_NOTES_{version}.md"
                self.assertTrue(path.exists(), path)
                text = path.read_text(encoding="utf-8")
                for phrase in ("What changed", "Safety", "Known limits"):
                    self.assertIn(phrase, text)
                self.assertIn("Reproduce", text)
                self.assertRegex(text, r"forbidden output|forbidden outputs|Forbidden", msg=version)

    def test_github_release_todo_lists_prepared_notes(self):
        text = (ROOT / "docs" / "GITHUB_RELEASE_TODO.md").read_text(encoding="utf-8")

        for version in (
            "v2.4.1",
            "v2.5.0",
            "v2.6.0",
            "v3.0.0",
            "v3.0.1",
            "v3.2.2",
            "v3.2.3",
            "v3.2.4",
            "v3.2.5",
            "v3.2.6",
            "v3.2.7",
            "v3.2.8",
            "v3.3.0",
            "v4.0.0",
            "v5.1.0",
        ):
            self.assertIn(version, text)
        self.assertIn("Publish releases only from the intended tags/commits", text)
        self.assertIn("v2.4.1", text)
        self.assertIn("published as latest stable", text)
        self.assertIn("v3.0.1", text)
        self.assertIn("v5.1.0", text)
        self.assertIn("https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v2.4.1", text)


if __name__ == "__main__":
    unittest.main()


