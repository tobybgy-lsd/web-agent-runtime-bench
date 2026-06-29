from __future__ import annotations

import json
import unittest
from pathlib import Path


class PuppeteerAdapterFixtureTests(unittest.TestCase):
    def test_puppeteer_fixture_set_has_expected_cases(self) -> None:
        root = Path("examples/cross_framework_fixtures/puppeteer")
        self.assertGreaterEqual(len([p for p in root.iterdir() if p.is_dir()]), 10)
        expected = json.loads((root / "proxy_failed" / "expected_diagnosis.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["technical_category"], "network_http_error")
        self.assertEqual(expected["subtype"], "proxy_connection_failed")


if __name__ == "__main__":
    unittest.main()
