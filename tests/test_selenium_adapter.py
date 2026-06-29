from __future__ import annotations

import json
import unittest
from pathlib import Path


class SeleniumAdapterFixtureTests(unittest.TestCase):
    def test_selenium_fixture_set_has_expected_cases(self) -> None:
        root = Path("examples/cross_framework_fixtures/selenium")
        self.assertGreaterEqual(len([p for p in root.iterdir() if p.is_dir()]), 8)
        expected = json.loads((root / "no_such_element" / "expected_diagnosis.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["technical_category"], "selector_drift")
        self.assertEqual(expected["subtype"], "selenium_no_such_element")


if __name__ == "__main__":
    unittest.main()
