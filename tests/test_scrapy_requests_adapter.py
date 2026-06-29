from __future__ import annotations

import json
import unittest
from pathlib import Path


class ScrapyRequestsAdapterFixtureTests(unittest.TestCase):
    def test_scrapy_requests_fixture_set_has_expected_cases(self) -> None:
        root = Path("examples/cross_framework_fixtures/scrapy_requests")
        self.assertGreaterEqual(len([p for p in root.iterdir() if p.is_dir()]), 15)
        expected = json.loads((root / "httpx_connect_error" / "expected_diagnosis.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["technical_category"], "network_http_error")
        self.assertEqual(expected["subtype"], "dns_name_not_resolved")


if __name__ == "__main__":
    unittest.main()
