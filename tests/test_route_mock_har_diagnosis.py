import json
import tempfile
import unittest
from pathlib import Path

from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.reporter import render_markdown_report
from trace_doctor.cli import write_trace_doctor_report


def route_artifact(run_id: str, observations: dict, message: str = "Playwright route or HAR mock did not satisfy request") -> dict:
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": run_id,
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "Playwright route/mock/HAR interception failed during a browser automation run.",
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


class RouteMockHarDiagnosisTests(unittest.TestCase):
    def test_classifies_route_pattern_mismatch(self):
        diagnosis = classify_failure_artifact(
            route_artifact(
                "PW_ROUTE_001",
                {
                    "route_registered": True,
                    "route_pattern": "**/api/products",
                    "request_url": "https://example.test/v2/products",
                    "route_matched": False,
                    "live_network_request": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        self.assertEqual(diagnosis["subtype"], "route_pattern_mismatch")
        self.assertEqual(diagnosis["evidence_level"], "confirmed")

    def test_classifies_route_registered_too_late(self):
        diagnosis = classify_failure_artifact(
            route_artifact(
                "PW_ROUTE_002",
                {
                    "route_registered_after_request": True,
                    "first_request_url": "https://example.test/api/cart",
                    "route_registered_at_ms": 850,
                    "first_request_at_ms": 120,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        self.assertEqual(diagnosis["subtype"], "route_registered_too_late")

    def test_classifies_har_not_found_or_not_loaded(self):
        diagnosis = classify_failure_artifact(
            route_artifact(
                "PW_ROUTE_003",
                {
                    "har_expected": True,
                    "har_loaded": False,
                    "har_path": "fixtures/api.har",
                    "har_error": "ENOENT: no such file or directory",
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        self.assertEqual(diagnosis["subtype"], "har_not_found_or_not_loaded")

    def test_classifies_har_fallback_network_leak(self):
        diagnosis = classify_failure_artifact(
            route_artifact(
                "PW_ROUTE_004",
                {
                    "har_loaded": True,
                    "har_not_found_policy": "fallback",
                    "har_miss_url": "https://example.test/api/search?q=demo",
                    "live_network_request": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        self.assertEqual(diagnosis["subtype"], "har_fallback_network_leak")

    def test_classifies_mock_response_shape_mismatch(self):
        diagnosis = classify_failure_artifact(
            route_artifact(
                "PW_ROUTE_005",
                {
                    "mock_response_fulfilled": True,
                    "mock_status": 200,
                    "expected_response_fields": ["items", "price"],
                    "actual_response_fields": ["data"],
                    "mock_response_shape_mismatch": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        self.assertEqual(diagnosis["subtype"], "mock_response_shape_mismatch")

    def test_route_mock_har_beats_generic_network_and_shape_diagnosis(self):
        diagnosis = classify_failure_artifact(
            route_artifact(
                "PW_ROUTE_PRIORITY",
                {
                    "har_loaded": True,
                    "har_not_found_policy": "fallback",
                    "har_miss_url": "https://example.test/api/search",
                    "live_network_request": True,
                    "status_code": 503,
                    "actual_response_fields": [],
                    "expected_response_fields": ["items"],
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_route_mock_har")
        alternatives = {item["failure_type"] for item in diagnosis.get("alternative_diagnoses", [])}
        self.assertIn("network_http_error", alternatives)

    def test_markdown_report_includes_subtype_and_evidence_level(self):
        artifact = route_artifact(
            "PW_ROUTE_REPORT",
            {
                "route_registered": True,
                "route_pattern": "**/api/products",
                "request_url": "https://example.test/v2/products",
                "route_matched": False,
                "live_network_request": True,
            },
        )
        diagnosis = classify_failure_artifact(artifact)

        report = render_markdown_report(diagnosis, artifact)

        self.assertIn("playwright_route_mock_har", report)
        self.assertIn("route_pattern_mismatch", report)
        self.assertIn("Evidence Level: `confirmed`", report)
        self.assertIn("route pattern did not match request URL", report)

    def test_trace_doctor_repair_suggestions_include_route_code_snippet(self):
        artifact = route_artifact(
            "PW_ROUTE_REPAIR",
            {
                "route_registered": True,
                "route_pattern": "**/api/products",
                "request_url": "https://example.test/v2/products",
                "route_matched": False,
                "live_network_request": True,
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "report"
            write_trace_doctor_report(out_dir, artifact, diagnosis)

            repair = (out_dir / "repair_suggestions.md").read_text(encoding="utf-8")
            issue = (out_dir / "issue_draft.md").read_text(encoding="utf-8")
            payload = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))

        self.assertIn("page.route('**/api/products/**'", repair)
        self.assertIn("route.fulfill", repair)
        self.assertIn("route_pattern_mismatch", issue)
        self.assertEqual(payload["evidence_level"], "confirmed")


if __name__ == "__main__":
    unittest.main()
