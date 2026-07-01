import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "examples" / "spiderbuf_inspired_challenges"
VALIDATION = ROOT / "validation" / "spiderbuf_inspired_validation.json"


EXPECTED_CASES = {
    "01_cookie_required",
    "02_iframe_extraction",
    "03_ajax_dynamic_loading",
    "04_random_css_class_selector_drift",
    "05_infinite_scroll_missing_items",
    "06_rate_limit_429",
    "07_api_signature_required",
    "08_browser_fingerprint_risk",
    "09_selenium_detection_risk",
    "10_challenge_page_detected",
    "11_ja3_fingerprint_mismatch",
    "12_hmac_signature_invalid",
    "13_slider_trajectory_rejection",
    "14_mfa_login_redirect",
    "15_data_poisoning_decoy_response",
    "16_header_normalization_evidence_gap",
    "17_stateful_session_lifecycle_anomaly",
}

class SpiderbufInspiredValidationTests(unittest.TestCase):
    def test_pack_has_required_local_only_structure(self):
        self.assertTrue(PACK_ROOT.exists())
        self.assertEqual({path.name for path in PACK_ROOT.iterdir() if path.is_dir()}, EXPECTED_CASES)
        self.assertTrue((PACK_ROOT / "README.md").exists())

        for case_id in sorted(EXPECTED_CASES):
            case_dir = PACK_ROOT / case_id
            for required in [
                "README.md",
                "source.json",
                "failed_run",
                "rerun_after_fix",
                "expected_diagnosis.json",
                "expected_fix_plan.json",
                "expected_verification.json",
            ]:
                self.assertTrue((case_dir / required).exists(), f"{case_id}/{required}")

            source = json.loads((case_dir / "source.json").read_text(encoding="utf-8"))
            self.assertEqual(source["source_project"], "hhuayuan/spiderbuf")
            self.assertTrue(source["local_only"], case_id)
            self.assertTrue(source["does_not_access_real_spiderbuf_site"], case_id)
            self.assertEqual(source["safe_boundary"], "diagnosis_only_no_bypass")

    def test_runner_generates_spiderbuf_inspired_validation(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_spiderbuf_inspired_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(VALIDATION.read_text(encoding="utf-8"))
        self.assertEqual(summary["version"], "v2.3")
        self.assertEqual(summary["track"], "spiderbuf_inspired_challenge_validation")
        self.assertGreaterEqual(summary["total_cases"], 10)
        self.assertGreaterEqual(summary["diagnosis_reasonable"], 9)
        self.assertGreaterEqual(summary["fix_plan_valid"], 10)
        self.assertGreaterEqual(summary["verification_correct"], 8)
        self.assertEqual(summary["forbidden_output_count"], 0)

    def test_docs_expose_spiderbuf_inspired_validation_track(self):
        dashboard = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Spiderbuf-inspired", dashboard)
        self.assertIn("run_spiderbuf_inspired_validation", dashboard)
        self.assertIn("Spiderbuf-inspired", readme)


if __name__ == "__main__":
    unittest.main()
