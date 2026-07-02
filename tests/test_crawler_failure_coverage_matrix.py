import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CrawlerFailureCoverageMatrixTests(unittest.TestCase):
    def test_crawler_failure_coverage_matrix_meets_p98_shape(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_crawler_failure_coverage_matrix"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path = ROOT / "validation" / "crawler_failure_coverage_matrix.json"
        self.assertTrue(path.exists())
        payload = json.loads(path.read_text(encoding="utf-8"))
        categories = payload["categories"]
        self.assertGreaterEqual(len(categories), 20)
        self.assertGreaterEqual(payload["total_mapped_cases"], 200)
        self.assertIn("gap_backlog", payload)
        for category in categories:
            self.assertIn("coverage_count", category)
            self.assertGreaterEqual(category["coverage_count"], 10)
            self.assertEqual(category["forbidden_output_count"], 0)


if __name__ == "__main__":
    unittest.main()

