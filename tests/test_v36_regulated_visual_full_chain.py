from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.agent_invocation import bootstrap_agent_frontend


ROOT = Path(__file__).resolve().parents[1]


class V36RegulatedVisualFullChainTests(unittest.TestCase):
    def test_cli_exposes_regulated_and_full_chain_commands(self) -> None:
        help_result = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stdout + help_result.stderr)
        self.assertIn("regulated-eval", help_result.stdout)
        self.assertIn("full-chain-eval", help_result.stdout)
        self.assertIn("visual-runtime", help_result.stdout)

        for command in ("regulated-eval", "full-chain-eval"):
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", command, "--help"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_regulated_eval_runs_finance_government_and_healthcare(self) -> None:
        for suite in ("finance", "government", "healthcare"):
            with tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "failure_doctor",
                        "regulated-eval",
                        "--suite",
                        suite,
                        "--out",
                        tmp,
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                payload = json.loads((Path(tmp) / "regulated_eval_result.json").read_text(encoding="utf-8"))
                self.assertEqual(payload["suite"], suite)
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["real_platform_access_count"], 0)
                self.assertEqual(payload["forbidden_output_count"], 0)
                self.assertGreaterEqual(payload["cases"], 60)

    def test_full_chain_eval_generates_report_and_blocks_unsafe_sharing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            failed_run = Path(tmp) / "failed_run"
            failed_run.mkdir()
            (failed_run / "error.log").write_text(
                "visual action used stale screenshot; ai handoff contains raw customer token and must be sanitized\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "report"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "full-chain-eval",
                    "--input",
                    str(failed_run),
                    "--out",
                    str(out),
                    "--include-safety",
                    "--include-visual",
                    "--include-regulated",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads((out / "full_chain_evaluation.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "full_chain_evaluation/v1")
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["unsafe_handoff_blocked"], True)
            self.assertEqual(payload["unsafe_share_blocked"], True)
            self.assertEqual(payload["external_api_call_count"], 0)

    def test_validation_runners_and_p98_gate_include_v36_pillars(self) -> None:
        for module in (
            "tools.validation.run_regulated_industry_validation",
            "tools.validation.run_visual_agent_runtime_validation",
            "tools.validation.run_full_chain_agent_evaluation",
            "tools.validation.run_p98_master_gate",
        ):
            result = subprocess.run([sys.executable, "-m", module], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        gate = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["version"], "v3.9.0")
        self.assertEqual(gate["current_stable_line"], "v3.9.0")
        self.assertEqual(gate["pillars"]["regulated_industry_workflow_pack"]["status"], "pass")
        self.assertEqual(gate["pillars"]["visual_agent_runtime_observability"]["status"], "pass")
        self.assertEqual(gate["pillars"]["full_chain_agent_evaluation"]["status"], "pass")

    def test_agent_bootstrap_writes_regulated_visual_and_full_chain_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            manifest = bootstrap_agent_frontend(project, target="codex")
            target_dir = project / ".failure-doctor" / "agents" / "codex"

            self.assertEqual(manifest["pack_version"], "3.9.0")
            self.assertTrue((target_dir / "regulated_workflow.md").exists())
            self.assertTrue((target_dir / "visual_runtime_workflow.md").exists())
            self.assertTrue((target_dir / "full_chain_evaluation_workflow.md").exists())
            self.assertIn("regulated-eval", manifest["regulated_eval_command"])
            self.assertIn("full-chain-eval", manifest["full_chain_eval_command"])


if __name__ == "__main__":
    unittest.main()
