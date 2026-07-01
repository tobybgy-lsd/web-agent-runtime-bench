import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.agent_invocation import AGENT_TARGETS, bootstrap_agent_frontend


class AgentFrontendInvocationTests(unittest.TestCase):
    def test_bootstrap_writes_all_first_class_and_workflow_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()

            manifest = bootstrap_agent_frontend(project, target="all")

            self.assertEqual(manifest["schema_version"], "agent_invocation_pack/v1")
            self.assertEqual(manifest["pack_version"], "3.3.0")
            self.assertEqual(set(manifest["targets"]), set(AGENT_TARGETS))
            self.assertTrue((project / ".failure-doctor" / "AGENT_ENTRYPOINT.md").exists())

            for target in AGENT_TARGETS:
                target_dir = project / ".failure-doctor" / "agents" / target
                self.assertTrue((target_dir / "instructions.md").exists(), target)
                self.assertTrue((target_dir / "diagnose_project.md").exists(), target)
                self.assertTrue((target_dir / "repair_workflow.md").exists(), target)
                self.assertTrue((target_dir / "allowed_commands.md").exists(), target)
                self.assertTrue((target_dir / "forbidden_actions.md").exists(), target)

            saved = json.loads((project / ".failure-doctor" / "agents" / "agent_invocation_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["target_count"], len(AGENT_TARGETS))

    def test_bootstrap_single_target_keeps_project_scoped_safety_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()

            manifest = bootstrap_agent_frontend(project, target="codex")

            self.assertEqual(manifest["targets"], ["codex"])
            entrypoint = (project / ".failure-doctor" / "AGENT_ENTRYPOINT.md").read_text(encoding="utf-8")
            instructions = (project / ".failure-doctor" / "agents" / "codex" / "instructions.md").read_text(encoding="utf-8")
            forbidden = (project / ".failure-doctor" / "agents" / "codex" / "forbidden_actions.md").read_text(encoding="utf-8")

            self.assertIn("failure-doctor collect --project . --preset auto --auto-diagnose --auto-handoff --auto-sanitize", entrypoint)
            self.assertIn("Codex", instructions)
            self.assertIn("project-scoped only", forbidden)
            self.assertIn("no browser profile access", forbidden)
            self.assertIn("no credential store access", forbidden)
            self.assertIn("no CAPTCHA bypass", forbidden)
            self.assertIn("no bot evasion", forbidden)

    def test_agent_bootstrap_cli_writes_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "agent-bootstrap",
                    "--target",
                    "generic_agent",
                    "--project",
                    str(project),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Agent Failure Doctor Frontend Invocation Pack", result.stdout)
            self.assertTrue((project / ".failure-doctor" / "agents" / "generic_agent" / "diagnose_project.md").exists())

    def test_docs_expose_agent_bootstrap_entrypoint(self):
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8", errors="replace")
        doc = (root / "docs" / "AGENT_FRONTEND_INVOCATION.md").read_text(encoding="utf-8", errors="replace")

        self.assertIn("failure-doctor agent-bootstrap", readme)
        self.assertIn("Agent Frontend Invocation Pack", doc)
        self.assertIn("codex", doc)
        self.assertIn("cursor", doc)
        self.assertIn("claude_code", doc)
        self.assertIn("hermes", doc)


if __name__ == "__main__":
    unittest.main()
