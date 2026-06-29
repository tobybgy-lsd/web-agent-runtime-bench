import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import diagnose_inputs, enrich_for_users
from tools.failure_artifacts.classifier import classify_failure_artifact


def base_artifact(message="", observations=None, status_code=200):
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": "evidence_scoring",
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "evidence scoring regression",
        "error": {"message": message, "stack": "", "status_code": status_code},
        "artifacts": {},
        "observations": observations or {},
        "expected": {"required_fields": []},
        "actual": {"fields": {}, "array_length": None},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
        },
    }


class ClassifierEvidenceScoringTests(unittest.TestCase):
    def test_proxy_mention_in_description_does_not_trigger_proxy_failure(self):
        artifact = base_artifact(
            "Timeout waiting for selector .submit",
            {
                "user_description": "I use proxy settings in my test environment.",
                "missing_selectors": [".submit"],
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        self.assertNotEqual(diagnosis["failure_type"], "network_http_error")

    def test_login_redirect_outranks_generic_timeout(self):
        artifact = base_artifact(
            "Timeout 30000ms exceeded after navigation",
            {
                "auth_redirect_detected": True,
                "redirected_to_login": True,
                "storage_context_evidence_level": "inferred",
                "auth_status_code": 302,
                "final_url": "http://127.0.0.1/login",
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["evidence_level"], "inferred")

    def test_route_from_har_error_outranks_generic_network_error(self):
        artifact = base_artifact(
            "net::ERR_FILE_NOT_FOUND while loading HAR",
            {
                "har_expected": True,
                "har_loaded": False,
                "har_path": "fixtures/api.har",
                "har_error": "net::ERR_FILE_NOT_FOUND",
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        self.assertEqual(diagnosis["subtype"], "har_not_found_or_not_loaded")

    def test_shadow_dom_inferred_evidence_is_not_confirmed(self):
        artifact = base_artifact(
            "locator.click: Timeout 30000ms exceeded",
            {
                "element_exists_in_shadow_dom": True,
                "ordinary_locator_failed": True,
                "shadow_inferred_from_html": True,
                "shadow_evidence_level": "inferred",
                "shadow_host": "my-widget",
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        self.assertEqual(diagnosis["evidence_level"], "inferred")

    def test_anti_bot_challenge_requires_structured_signal_for_high_confidence(self):
        description_only = base_artifact(
            "",
            {"user_description": "The user mentioned captcha in a planning note, but no page body or status showed it."},
        )
        diagnosis = classify_failure_artifact(description_only)
        self.assertNotEqual(diagnosis["failure_type"], "anti_bot_risk")

        structured = base_artifact(
            "",
            {"body_text": "Verify you are human before continuing", "status_code": 403},
            status_code=403,
        )
        structured_result = classify_failure_artifact(structured)
        self.assertEqual(structured_result["failure_type"], "anti_bot_risk")

    def test_challenge_url_path_does_not_trigger_anti_bot_without_page_signal(self):
        artifact = base_artifact(
            "FileNotFoundError: [Errno 2] No such file or directory: './data/e03/e03_1.html'",
            {
                "network_events": [
                    {
                        "url": "https://spiderbuf.cn/challenge/scraping-random-pagination/2fe6286a4e5f",
                        "status": 200,
                    }
                ],
                "log_excerpt": "pagination links were present before local file write failed",
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        self.assertEqual(diagnosis["failure_type"], "toolchain_environment")

    def test_local_file_error_outranks_selector_like_html_noise(self):
        artifact = base_artifact(
            "FileNotFoundError: [Errno 2] No such file or directory: './data/e03/e03_1.html'",
            {
                "log_excerpt": (
                    "FileNotFoundError: [Errno 2] No such file or directory: './data/e03/e03_1.html'\n"
                    "<html><input[name=username]><script>selector not found</script></html>"
                ),
                "user_description": "The page HTML was printed before a local output file write failed.",
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        self.assertEqual(diagnosis["failure_type"], "toolchain_environment")

    def test_forbidden_bypass_terms_never_appear_in_report_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            out_dir = Path(tmp) / "report"
            case_dir.mkdir()
            (case_dir / "error.log").write_text("HTTP 429 too many requests\n", encoding="utf-8")
            args = type("Args", (), {"input": str(case_dir), "out": str(out_dir), "run_id": "safety_case"})
            self.assertEqual(diagnose_inputs(args), 0)
            combined = "\n".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in out_dir.iterdir()
                if path.suffix in {".md", ".json"}
            ).lower()
            for forbidden in (
                "captcha bypass",
                "bot evasion",
                "spoof fingerprint",
                "crack signature",
                "bypass cloudflare",
                "ip pool",
                "account pool",
            ):
                self.assertNotIn(forbidden, combined)
