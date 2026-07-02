import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHOWCASE_REPORT = ROOT / "sample_reports" / "composite_showcase" / "auth_redirect_plus_selector_timeout"


class AiHandoffPatchProposalTests(unittest.TestCase):
    def test_handoff_generates_ai_ready_task_pack_for_all_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "ai_handoff"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "handoff",
                    str(SHOWCASE_REPORT),
                    "--target",
                    "codex",
                    "--out",
                    str(out_dir),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            expected_files = {
                "ai_handoff.json",
                "ai_handoff.md",
                "codex_task.md",
                "claude_code_task.md",
                "cursor_task.md",
                "affected_files.json",
                "validation_commands.md",
                "forbidden_actions.md",
                "token_budget_report.json",
                "ai_handoff_pack.zip",
            }
            self.assertTrue(expected_files.issubset({path.name for path in out_dir.iterdir()}))

            task = (out_dir / "codex_task.md").read_text(encoding="utf-8")
            self.assertIn("playwright_storage_state_context", task)
            self.assertIn("Repair order", task)
            self.assertIn("Do not apply changes automatically", task)
            self.assertIn("failure-doctor verify", task)

            summary = json.loads((out_dir / "ai_handoff.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["schema_version"], "ai_handoff/v1")
            self.assertEqual(summary["selected_target"], "codex")
            self.assertEqual(summary["technical_category"], "playwright_storage_state_context")
            self.assertTrue(summary["tasks"]["codex"])
            self.assertTrue(summary["required_sections_present"])

            overview = (out_dir / "ai_handoff.md").read_text(encoding="utf-8")
            self.assertIn("# AI Handoff", overview)
            self.assertIn("Repair order", overview)
            self.assertIn("Forbidden actions", overview)

            token_budget = json.loads((out_dir / "token_budget_report.json").read_text(encoding="utf-8"))
            self.assertEqual(token_budget["selected_target"], "codex")
            self.assertGreater(token_budget["estimated_input_tokens"], 0)
            self.assertLessEqual(token_budget["estimated_input_tokens"], token_budget["recommended_budget"])

    def test_propose_patch_generates_dry_run_patch_plan_without_modifying_repo(self):
        before_status = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        ).stdout
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "patch_plan"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "propose-patch",
                    "--repo",
                    str(ROOT),
                    "--report",
                    str(SHOWCASE_REPORT),
                    "--out",
                    str(out_dir),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            expected_files = {
                "patch_proposal.md",
                "proposed_changes.json",
                "affected_files.json",
                "validation_commands.md",
                "patch_risk_assessment.json",
            }
            self.assertTrue(expected_files.issubset({path.name for path in out_dir.iterdir()}))

            proposed = json.loads((out_dir / "proposed_changes.json").read_text(encoding="utf-8"))
            self.assertTrue(proposed["dry_run_only"])
            self.assertEqual(proposed["source_report"], str(SHOWCASE_REPORT))
            self.assertTrue(proposed["change_steps"])
            self.assertFalse(proposed["applied"])

            risk = json.loads((out_dir / "patch_risk_assessment.json").read_text(encoding="utf-8"))
            self.assertEqual(risk["mode"], "proposal_only")
            self.assertFalse(risk["auto_apply"])
            self.assertIn("access-control defeat", risk["forbidden_actions"])

        after_status = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        ).stdout
        self.assertEqual(after_status, before_status)

    def test_ai_handoff_validation_ledger_meets_v2_5_thresholds(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_ai_handoff_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        ledger_path = ROOT / "validation" / "ai_handoff_validation.json"
        self.assertTrue(ledger_path.exists())
        payload = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 20)
        self.assertEqual(payload["codex_tasks_generated"], payload["total_cases"])
        self.assertEqual(payload["claude_code_tasks_generated"], payload["total_cases"])
        self.assertEqual(payload["cursor_tasks_generated"], payload["total_cases"])
        self.assertGreaterEqual(payload["patch_proposals_generated"], 15)
        self.assertEqual(payload["required_sections_present"], payload["total_cases"])
        self.assertGreaterEqual(payload["concise_token_budget_pass"], 18)
        self.assertEqual(payload["forbidden_output_count"], 0)


if __name__ == "__main__":
    unittest.main()

