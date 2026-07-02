import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.auto_collect import collect_project


class AutoCollectorPipelineTests(unittest.TestCase):
    def test_auto_diagnose_plan_handoff_sanitize_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "error.log").write_text(
                "net::ERR_PROXY_CONNECTION_FAILED while page.goto https://example.invalid\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "auto_report"

            manifest = collect_project(
                root,
                out,
                preset="auto",
                auto_diagnose=True,
                auto_handoff=True,
                auto_sanitize=True,
            )

            self.assertEqual(manifest["pipeline"]["auto_diagnose"], True)
            self.assertTrue((out / "report" / "diagnosis.json").exists())
            self.assertTrue((out / "fix_plan" / "fix_plan.json").exists())
            self.assertTrue((out / "ai_handoff" / "codex_task.md").exists())
            self.assertTrue((out / "ai_handoff" / "ai_handoff_pack.zip").exists())
            self.assertTrue((out / "sanitized_failure_pack" / "redaction_report.json").exists())
            diagnosis = json.loads((out / "report" / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertIn("next_action", diagnosis)


