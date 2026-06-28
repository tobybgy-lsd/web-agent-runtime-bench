import json
import tempfile
import unittest
from pathlib import Path

from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.reporter import render_markdown_report
from trace_doctor.cli import write_trace_doctor_report


def shadow_artifact(run_id: str, observations: dict, message: str = "Timeout waiting for selector inside shadow DOM") -> dict:
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": run_id,
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "Playwright locator failed around a custom element or shadow DOM boundary.",
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


class ShadowDomLocatorDiagnosisTests(unittest.TestCase):
    def test_classifies_shadow_root_boundary(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_001",
                {
                    "shadow_host": "my-component",
                    "shadow_root_mode": "open",
                    "inner_selector": "button.submit",
                    "element_exists_in_shadow_dom": True,
                    "ordinary_locator_failed": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        self.assertEqual(diagnosis["subtype"], "shadow_root_boundary")
        self.assertEqual(diagnosis["evidence_level"], "confirmed")

    def test_classifies_closed_shadow_root_unreachable(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_002",
                {
                    "shadow_host": "secure-widget",
                    "shadow_root_mode": "closed",
                    "inner_selector": "button",
                    "ordinary_locator_failed": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        self.assertEqual(diagnosis["subtype"], "closed_shadow_root_unreachable")

    def test_classifies_custom_element_not_upgraded(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_003",
                {
                    "custom_element_tag": "checkout-button",
                    "custom_element_defined": False,
                    "custom_element_upgraded": False,
                    "shadow_host": "checkout-button",
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        self.assertEqual(diagnosis["subtype"], "custom_element_not_upgraded")

    def test_classifies_locator_targets_host_not_inner_node(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_004",
                {
                    "locator_target": "my-component",
                    "intended_inner_selector": "button.buy",
                    "host_locator_clicked": True,
                    "inner_node_not_targeted": True,
                    "shadow_host": "my-component",
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        self.assertEqual(diagnosis["subtype"], "locator_targets_host_not_inner_node")

    def test_classifies_testid_inside_shadow_dom_missing_strategy(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_005",
                {
                    "testid": "submit-button",
                    "testid_inside_shadow_dom": True,
                    "missing_shadow_strategy": True,
                    "ordinary_locator_failed": True,
                },
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        self.assertEqual(diagnosis["subtype"], "testid_inside_shadow_dom_missing_strategy")

    def test_shadow_dom_beats_generic_selector_drift(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_PRIORITY",
                {
                    "shadow_host": "my-component",
                    "shadow_root_mode": "open",
                    "inner_selector": "button.submit",
                    "element_exists_in_shadow_dom": True,
                    "ordinary_locator_failed": True,
                    "missing_selectors": ["button.submit"],
                },
                message="Timeout waiting for selector button.submit",
            )
        )

        self.assertEqual(diagnosis["failure_type"], "playwright_shadow_dom_locator")
        alternatives = {item["failure_type"] for item in diagnosis.get("alternative_diagnoses", [])}
        self.assertIn("selector_drift", alternatives)

    def test_markdown_report_explains_element_exists_but_locator_path_unreachable(self):
        artifact = shadow_artifact(
            "PW_SHADOW_REPORT",
            {
                "shadow_host": "my-component",
                "shadow_root_mode": "open",
                "inner_selector": "button.submit",
                "element_exists_in_shadow_dom": True,
                "ordinary_locator_failed": True,
            },
        )
        diagnosis = classify_failure_artifact(artifact)

        report = render_markdown_report(diagnosis, artifact)

        self.assertIn("playwright_shadow_dom_locator", report)
        self.assertIn("shadow_root_boundary", report)
        self.assertIn("Evidence Level: `confirmed`", report)
        self.assertIn("element exists inside shadow DOM, but the ordinary locator path was unreachable", report)

    def test_trace_doctor_repair_suggestions_include_shadow_dom_code_snippet(self):
        artifact = shadow_artifact(
            "PW_SHADOW_REPAIR",
            {
                "shadow_host": "my-component",
                "shadow_root_mode": "open",
                "inner_selector": "button.submit",
                "element_exists_in_shadow_dom": True,
                "ordinary_locator_failed": True,
            },
        )
        diagnosis = classify_failure_artifact(artifact)
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "report"
            write_trace_doctor_report(out_dir, artifact, diagnosis)

            repair = (out_dir / "repair_suggestions.md").read_text(encoding="utf-8")
            issue = (out_dir / "issue_draft.md").read_text(encoding="utf-8")
            payload = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))

        self.assertIn("page.locator('my-component').locator('button.submit')", repair)
        self.assertIn("page.getByTestId('submit-button')", repair)
        self.assertIn("shadow_root_boundary", issue)
        self.assertEqual(payload["evidence_level"], "confirmed")

    def test_closed_shadow_root_repair_suggestion_is_careful(self):
        diagnosis = classify_failure_artifact(
            shadow_artifact(
                "PW_SHADOW_CLOSED_REPAIR",
                {
                    "shadow_host": "secure-widget",
                    "shadow_root_mode": "closed",
                    "inner_selector": "button",
                    "ordinary_locator_failed": True,
                },
            )
        )

        self.assertIn("Closed shadow root cannot be directly queried", "\n".join(diagnosis["suggested_fix"]))


if __name__ == "__main__":
    unittest.main()
