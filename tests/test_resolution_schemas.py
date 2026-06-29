import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResolutionSchemaTests(unittest.TestCase):
    def test_fix_plan_schema_has_required_fields(self):
        schema = json.loads((ROOT / "schemas" / "fix_plan.schema.json").read_text(encoding="utf-8"))
        required = set(schema["required"])
        for field in (
            "schema_version",
            "diagnosis_id",
            "failure_type",
            "technical_category",
            "subtype",
            "failure_layer",
            "root_cause",
            "fix_intent",
            "recommended_change_area",
            "expected_evidence_to_disappear",
            "expected_evidence_to_appear",
            "verification_strategy",
            "risk",
            "safe_next_action",
            "forbidden_actions",
        ):
            self.assertIn(field, required)

    def test_verification_report_schema_has_required_fields(self):
        schema = json.loads((ROOT / "schemas" / "verification_report.schema.json").read_text(encoding="utf-8"))
        required = set(schema["required"])
        for field in (
            "schema_version",
            "status",
            "before",
            "after",
            "resolved_evidence",
            "remaining_evidence",
            "new_failures",
            "confidence",
            "regression_case_created",
            "notes",
        ):
            self.assertIn(field, required)


if __name__ == "__main__":
    unittest.main()
