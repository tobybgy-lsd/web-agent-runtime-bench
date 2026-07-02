from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "failure_doctor", *args],
        cwd=str(cwd or ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class PluginSdkV42Tests(unittest.TestCase):
    def test_plugin_cli_scaffold_validate_install_enable_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "toy_adapter"
            workspace = root / ".failure-doctor-plugins"
            sample = root / "sample_artifacts"
            sample.mkdir()
            (sample / "error.log").write_text("selector timeout in toy framework\n", encoding="utf-8")
            out = root / "plugin_report"

            help_result = run_cli("plugin", "--help")
            self.assertEqual(help_result.returncode, 0, help_result.stderr + help_result.stdout)
            self.assertIn("scaffold", help_result.stdout)

            scaffold = run_cli(
                "plugin",
                "scaffold",
                "--type",
                "framework-adapter",
                "--name",
                "toy_adapter",
                "--out",
                str(plugin),
            )
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr + scaffold.stdout)
            self.assertTrue((plugin / "plugin_manifest.json").exists())
            self.assertTrue((plugin / "FORBIDDEN_ACTIONS.md").exists())

            validate = run_cli("plugin", "validate", str(plugin))
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)
            report = json.loads((plugin / "plugin_validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["risk_level"], "low")

            install = run_cli("plugin", "install", str(plugin), "--workspace", str(workspace))
            self.assertEqual(install.returncode, 0, install.stderr + install.stdout)
            enable = run_cli("plugin", "enable", "toy_adapter", "--workspace", str(workspace))
            self.assertEqual(enable.returncode, 0, enable.stderr + enable.stdout)
            listed = run_cli("plugin", "list", "--workspace", str(workspace))
            self.assertEqual(listed.returncode, 0, listed.stderr + listed.stdout)
            self.assertIn("toy_adapter", listed.stdout)

            ran = run_cli(
                "plugin",
                "run",
                "toy_adapter",
                "--workspace",
                str(workspace),
                "--input",
                str(sample),
                "--out",
                str(out),
            )
            self.assertEqual(ran.returncode, 0, ran.stderr + ran.stdout)
            payload = json.loads((out / "plugin_result.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["plugin_id"], "toy_adapter")
            self.assertTrue(payload["schema_valid"])
            self.assertIn("evidence_items", payload)

    def test_unsafe_plugins_are_blocked_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "unsafe_plugin"
            plugin.mkdir()
            manifest = {
                "schema_version": "failure_doctor_plugin/v1",
                "plugin_id": "unsafe_plugin",
                "name": "Unsafe Plugin",
                "version": "0.1.0",
                "type": "diagnosis-rule",
                "entrypoint": "plugin.py",
                "description": "tries to use network and private content",
                "local_only": True,
                "no_upload": True,
                "no_external_api": True,
                "requires_network": True,
                "requires_shell": True,
                "requires_write_access": False,
                "permissions": ["read_input_dir", "network_access", "run_local_command"],
                "hooks": ["diagnose.rule_candidate"],
                "safety": {
                    "forbidden_actions_declared": True,
                    "raw_secret_handling": "redact",
                    "private_solution_allowed": False,
                    "bypass_guidance_allowed": False,
                },
            }
            (plugin / "plugin_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (plugin / "plugin.py").write_text("RECOMMENDATION='captcha bypass with FLAG private solver'\n", encoding="utf-8")

            validate = run_cli("plugin", "validate", str(plugin))
            self.assertNotEqual(validate.returncode, 0)
            report = json.loads((plugin / "plugin_validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "fail")
            self.assertTrue(report["unsafe_plugin_blocked"])
            self.assertIn("network_access", "\n".join(report["blocking_issues"]))

            install = run_cli("plugin", "install", str(plugin), "--workspace", str(root / "plugins_ws"))
            self.assertNotEqual(install.returncode, 0)

    def test_collect_and_diagnose_accept_plugin_candidates_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "rules"
            workspace = root / "ws"
            failed = root / "failed"
            failed.mkdir()
            (failed / "error.log").write_text("ERP export missing approved_by column\n", encoding="utf-8")
            report = root / "report"

            self.assertEqual(
                run_cli("plugin", "scaffold", "--type", "diagnosis-rule", "--name", "erp_rules", "--out", str(plugin)).returncode,
                0,
            )
            self.assertEqual(run_cli("plugin", "install", str(plugin), "--workspace", str(workspace)).returncode, 0)
            self.assertEqual(run_cli("plugin", "enable", "erp_rules", "--workspace", str(workspace)).returncode, 0)

            diagnosed = run_cli(
                "diagnose",
                str(failed),
                "--plugin",
                "erp_rules",
                "--plugins",
                str(workspace),
                "--out",
                str(report),
            )
            self.assertEqual(diagnosed.returncode, 0, diagnosed.stderr + diagnosed.stdout)
            diagnosis = json.loads((report / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertIn("plugin_candidates", diagnosis)
            self.assertEqual(diagnosis["plugin_candidates"][0]["plugin_id"], "erp_rules")
            self.assertNotEqual(diagnosis.get("subtype"), "erp_rules")


if __name__ == "__main__":
    unittest.main()
