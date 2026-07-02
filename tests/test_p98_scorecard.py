import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P98ScorecardTests(unittest.TestCase):
    def test_p98_scorecard_documents_controlled_maturity_gates(self):
        path = ROOT / "docs" / "P98_CONTROLLED_MATURITY_SCORECARD.md"

        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("P98 Pillars", text)
        self.assertIn("forbidden_output_count = 0", text)
        self.assertIn("本评分不计算生态成熟度", text)
        self.assertIn("no real-platform access", text)
        self.assertIn("no private solution leakage", text)


if __name__ == "__main__":
    unittest.main()

