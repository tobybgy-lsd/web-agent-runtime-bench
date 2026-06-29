from __future__ import annotations

import json
import unittest
from pathlib import Path


class CypressAdapterFixtureTests(unittest.TestCase):
    def test_cypress_fixture_set_has_expected_cases(self) -> None:
        root = Path("examples/cross_framework_fixtures/cypress")
        self.assertGreaterEqual(len([p for p in root.iterdir() if p.is_dir()]), 9)
        expected = json.loads((root / "intercept_not_matched" / "expected_diagnosis.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["technical_category"], "playwright_route_mock_har")
        self.assertEqual(expected["subtype"], "cypress_intercept_not_matched")


if __name__ == "__main__":
    unittest.main()
