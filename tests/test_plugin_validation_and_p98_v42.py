from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.agent_invocation import bootstrap_agent_frontend


ROOT = Path(__file__).resolve().parents[1]


class PluginValidationAndP98V42Tests(unittest.TestCase):
    def test_plugin_validation_runner_and_p98_pillars_pass(self) -> None:
        validation = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_plugin_sdk_ecosystem_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(validation.returncode, 0, validation.stderr + validation.stdout)
        payload = json.loads((ROOT / "validation" / "plugin_sdk_ecosystem_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v4.2.0")
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 220)
        self.assertEqual(payload["unsafe_plugin_blocked"], payload["negative_unsafe_plugin_cases"])
        self.assertEqual(payload["external_api_call_count"], 0)
        self.assertEqual(payload["private_solution_leak_count"], 0)

        p98 = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_p98_master_gate"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        self.assertEqual(p98.returncode, 0, p98.stderr + p98.stdout)
        gate = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["version"], "v5.2.0")
        self.assertEqual(gate["overall_status"], "pass")
        self.assertEqual(gate["pillars"]["plugin_sdk_ecosystem"]["status"], "pass")
        self.assertEqual(gate["pillars"]["plugin_security_sandbox"]["status"], "pass")
        self.assertEqual(gate["pillars"]["adapter_extension_api"]["status"], "pass")

    def test_agent_bootstrap_includes_plugin_sdk_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = bootstrap_agent_frontend(Path(tmp), "codex")
            target = Path(tmp) / ".failure-doctor" / "agents" / "codex"
            workflow = target / "plugin_sdk_workflow.md"
            self.assertTrue(workflow.exists())
            body = workflow.read_text(encoding="utf-8")
            self.assertIn("Validate plugin manifest first", body)
            self.assertIn("plugins as candidates", body)
            self.assertIn("Do not allow plugins to bypass safety gate", body)
            self.assertIn("plugin_sdk_command", manifest)


if __name__ == "__main__":
    unittest.main()

