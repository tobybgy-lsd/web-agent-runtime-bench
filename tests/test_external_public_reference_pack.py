import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExternalPublicReferencePackTests(unittest.TestCase):
    def test_seed_and_external_reference_ledger_have_62_sources(self):
        seed = json.loads((ROOT / "validation" / "source_ledger_external_seed_v0_9.json").read_text(encoding="utf-8"))
        ledger = json.loads((ROOT / "validation" / "external_public_reference_ledger.json").read_text(encoding="utf-8"))

        self.assertEqual(seed["count"], 62)
        self.assertEqual(len(seed["sources"]), 62)
        self.assertEqual(ledger["summary"]["total_sources"], 62)
        self.assertEqual(ledger["summary"]["official_doc_pattern"], 5)
        self.assertGreaterEqual(ledger["summary"]["real_public_issue"], 40)
        self.assertGreaterEqual(ledger["summary"]["real_public_qa"], 10)

        for source in ledger["sources"]:
            self.assertIn(source["source_type"], {"real_public_issue", "real_public_qa", "official_doc_pattern"})
            self.assertIn(source["validation_use"], {"external_public_reference", "official_doc_pattern"})
            self.assertIn("source_url", source)
            self.assertIn("title", source)
            self.assertIn("expected_diagnosis", source)
            self.assertLessEqual(len(source.get("summary", "")), 240)

    def test_external_heldout_20_is_reproducible_and_safe(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_external_public_reference_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        data = json.loads((ROOT / "validation" / "external_heldout_20.json").read_text(encoding="utf-8"))
        summary = data["summary"]
        self.assertEqual(summary["total_heldout_cases"], 20)
        self.assertGreaterEqual(summary["reasonable_category_match"], 15)
        self.assertGreaterEqual(summary["actionable_next_action"], 17)
        self.assertEqual(summary["forbidden_output_count"], 0)
        self.assertIn("regression_backlog", data)

        for case in data["cases"]:
            self.assertEqual(case["validation_use"], "external_public_reference")
            self.assertIn(case["result"], {"exact_match", "category_match", "insufficient_evidence", "severe_misclassification"})
            self.assertTrue(case["source_url"].startswith("https://"))

    def test_external_data_sources_doc_explains_boundaries(self):
        text = (ROOT / "docs" / "EXTERNAL_DATA_SOURCES.md").read_text(encoding="utf-8")
        for phrase in (
            "62 external public reference seeds",
            "not submitted to this repository by external users",
            "external_public_reference",
            "official_doc_pattern",
            "Anti-bot risk samples are identification and compliant routing only",
            "Do not copy long issue content",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
