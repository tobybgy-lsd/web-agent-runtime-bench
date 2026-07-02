from __future__ import annotations

import unittest
from pathlib import Path

from tools.validation.run_documentation_demo_adoption_validation import build_payload

ROOT = Path(__file__).resolve().parents[1]


class DocumentationAdoptionTests(unittest.TestCase):
    def test_required_docs_and_gallery_are_public_safe(self) -> None:
        payload = build_payload()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["no_raw_secret_in_docs"], 0)
        self.assertEqual(payload["no_private_solution_in_docs"], 0)
        self.assertGreaterEqual(payload["sample_report_count"], 9)


if __name__ == "__main__":
    unittest.main()

