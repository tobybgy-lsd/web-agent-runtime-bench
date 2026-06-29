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


if __name__ == "__main__":
    unittest.main()
