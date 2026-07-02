import json
import tempfile
import unittest
from pathlib import Path

from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.reporter import render_markdown_report
from trace_doctor.cli import write_trace_doctor_report


def storage_artifact(run_id: str, observations: dict, message: str = "Authenticated request redirected to login") -> dict:
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": run_id,
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "Playwright authenticated flow lost browser context state.",
        "error": {"message": message, "stack": "", "status_code": observations.get("status_code", 200)},
        "artifacts": {"notes": "notes.md"},
        "observations": observations,
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


class StorageStateContextDiagnosisTests(unittest.TestCase):
    def test_classifies_cookie_domain_mismatch(self):
        diagnosis = classify_failure_artifact(
            storage_artifact(
                "PW_STORAGE_001",
                {
                    "storage_state_loaded": True,
                    "current_host": "app.example.test",
                    "cookie_domain": "auth.example.test",
                    "missing_cookie_names": ["session"],
                    "response_chain": [{"url": "/account", "status": 302}, {"url": "/login", "status": 200}],
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["subtype"], "cookie_domain_mismatch")
        self.assertGreaterEqual(diagnosis["confidence"], 0.85)

    def test_classifies_storage_state_not_loaded(self):
        diagnosis = classify_failure_artifact(
            storage_artifact(
                "PW_STORAGE_002",
                {
                    "storage_state_expected": True,
                    "storage_state_loaded": False,
                    "missing_cookie_names": ["session"],
                    "final_url": "https://example.test/login",
                    "status_code": 401,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["subtype"], "storage_state_not_loaded")

    def test_classifies_context_recreated_without_state(self):
        diagnosis = classify_failure_artifact(
            storage_artifact(
                "PW_STORAGE_003",
                {
                    "context_recreated": True,
                    "new_context_storage_state": None,
                    "previous_authenticated_context": True,
                    "redirected_to_login": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["subtype"], "context_recreated_without_state")

    def test_classifies_local_storage_missing(self):
        diagnosis = classify_failure_artifact(
            storage_artifact(
                "PW_STORAGE_004",
                {
                    "storage_state_loaded": True,
                    "expected_local_storage_keys": ["auth:user", "auth:session"],
                    "missing_local_storage_keys": ["auth:session"],
                    "final_url": "https://example.test/login",
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["subtype"], "local_storage_missing")

    def test_classifies_base_url_state_origin_mismatch(self):
        diagnosis = classify_failure_artifact(
            storage_artifact(
                "PW_STORAGE_005",
                {
                    "base_url": "https://app.example.test",
                    "storage_state_origin": "https://staging.example.test",
                    "storage_state_loaded": True,
                    "missing_cookie_names": ["session"],
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["subtype"], "base_url_state_origin_mismatch")

    def test_storage_context_beats_generic_auth_and_network_diagnosis(self):
        diagnosis = classify_failure_artifact(
            storage_artifact(
                "PW_STORAGE_PRIORITY",
                {
                    "storage_state_expected": True,
                    "storage_state_loaded": False,
                    "final_url": "https://example.test/login",
                    "html_excerpt": "<input type=\"password\" />",
                    "status_code": 401,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")
        alternatives = {item["failure_type"] for item in diagnosis.get("alternative_diagnoses", [])}
        self.assertIn("auth_expiry", alternatives)
        self.assertIn("network_http_error", alternatives)

    def test_markdown_report_includes_subtype_and_evidence_chain(self):
        artifact = storage_artifact(
            "PW_STORAGE_REPORT",
            {
                "storage_state_expected": True,
                "storage_state_loaded": False,
                "missing_cookie_names": ["session"],
                "final_url": "https://example.test/login",
            },
        )
        diagnosis = classify_failure_artifact(artifact)

        report = render_markdown_report(diagnosis, artifact)

        self.assertIn("playwright_storage_state_context", report)
        self.assertIn("storage_state_not_loaded", report)
        self.assertIn("storageState was expected but not observed as loaded", report)

    def test_trace_doctor_repair_suggestions_include_playwright_code_snippet(self):
        artifact = storage_artifact(
            "PW_STORAGE_REPAIR",
            {
                "storage_state_expected": True,
                "storage_state_loaded": False,
                "missing_cookie_names": ["session"],
                "final_url": "https://example.test/login",
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "report"
            write_trace_doctor_report(out_dir, artifact, diagnosis)

            repair = (out_dir / "repair_suggestions.md").read_text(encoding="utf-8")
            issue = (out_dir / "issue_draft.md").read_text(encoding="utf-8")
            payload = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))

        self.assertIn("browser.newContext({ storageState", repair)
        self.assertIn("expect(page).not.toHaveURL", repair)
        self.assertIn("storage_state_not_loaded", issue)
        self.assertEqual(payload["subtype"], "storage_state_not_loaded")


if __name__ == "__main__":
    unittest.main()

