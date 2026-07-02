import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "validation" / "source_ledger_real_failures.json"

ALLOWED_SOURCE_TYPES = {
    "official_doc_pattern",
    "real_public_issue",
    "public_inspired_sanitized",
    "local_reproduction_from_public_pattern",
}

ALLOWED_CATEGORIES = {
    "storage_state_context",
    "route_mock_har",
    "shadow_dom_locator",
    "strict_mode",
    "timeout_navigation",
    "execution_context_destroyed",
    "download_popup",
    "service_worker_cache",
    "browser_environment",
    "agent_loop",
    "website_change",
    "anti_bot_risk",
    "network_proxy_dns_tls",
    "official_behavior_boundary",
}


class SourceLedgerRealFailuresTests(unittest.TestCase):
    def test_source_ledger_exists_and_has_required_real_data_counts(self):
        self.assertTrue(LEDGER.exists(), "validation/source_ledger_real_failures.json is required")
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        sources = ledger.get("sources", [])
        self.assertGreaterEqual(len(sources), 100)
        real_public = [item for item in sources if item.get("source_type") == "real_public_issue"]
        official_docs = [item for item in sources if item.get("source_type") == "official_doc_pattern"]
        self.assertGreaterEqual(len(real_public), 40)
        self.assertGreaterEqual(len(official_docs), 10)

    def test_source_records_are_structured_and_honestly_labeled(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        seen_ids = set()
        for item in ledger.get("sources", []):
            with self.subTest(source=item.get("id")):
                self.assertIn("id", item)
                self.assertNotIn(item["id"], seen_ids)
                seen_ids.add(item["id"])
                self.assertIn(item.get("source_type"), ALLOWED_SOURCE_TYPES)
                self.assertIn(item.get("category"), ALLOWED_CATEGORIES)
                self.assertIsInstance(item.get("expected_diagnosis"), dict)
                self.assertIn("technical_category", item["expected_diagnosis"])
                self.assertIn("subtype", item["expected_diagnosis"])
                source_url = str(item.get("source_url") or "")
                if source_url:
                    self.assertNotRegex(source_url, re.compile(r"example\.(com|local)|fake\.local", re.I))
                if item.get("source_type") == "public_inspired_sanitized":
                    self.assertFalse(
                        source_url.startswith("https://github.com/") and "/issues/" in source_url,
                        "public-inspired sanitized records must not pretend to be real GitHub issues",
                    )


