import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CompositeP95SchemaAndCliTests(unittest.TestCase):
    def test_composite_schema_files_define_required_sections(self):
        composite_schema = ROOT / "schemas" / "composite_diagnosis.schema.json"
        graph_schema = ROOT / "schemas" / "evidence_graph.schema.json"
        validation_schema = ROOT / "schemas" / "composite_validation_result.schema.json"
        for path in (composite_schema, graph_schema, validation_schema):
            self.assertTrue(path.exists(), path)

        schema = json.loads(composite_schema.read_text(encoding="utf-8"))
        properties = schema["properties"]
        for key in (
            "primary_failure",
            "secondary_failures",
            "blocking_failure",
            "evidence_graph",
            "repair_order",
            "score_breakdown",
            "safe_next_action",
        ):
            self.assertIn(key, properties)

    def test_diagnose_writes_legacy_and_composite_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_dir = root / "failed_run"
            out_dir = root / "report"
            case_dir.mkdir()
            (case_dir / "error.log").write_text(
                "locator.click: Timeout waiting for selector .price\n",
                encoding="utf-8",
            )
            (case_dir / "network.json").write_text(
                json.dumps([{"status": 302, "url": "https://example.test/login"}]),
                encoding="utf-8",
            )
            (case_dir / "user_description.txt").write_text(
                "The authenticated product page redirected to login before .price was found.",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(case_dir), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertIn("technical_category", diagnosis)
            self.assertIn("diagnosis_mode", diagnosis)
            self.assertIn("primary_failure", diagnosis)
            self.assertIn("repair_order", diagnosis)
            self.assertEqual(diagnosis["primary_failure"]["technical_category"], diagnosis["technical_category"])
            self.assertIn("Composite Diagnosis", (out_dir / "diagnosis.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

