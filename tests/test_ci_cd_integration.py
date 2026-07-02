from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CiCdIntegrationTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "failure_doctor", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_ci_run_writes_gate_and_summary_for_safe_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "report"
            report.mkdir()
            (report / "diagnosis.json").write_text(
                json.dumps(
                    {
                        "failure_type": "network_proxy",
                        "subtype": "proxy_connection_failed",
                        "confidence": 0.87,
                        "user_facing_category": "网络/代理问题",
                        "next_action": "Check authorized proxy settings and rerun the workflow.",
                    }
                ),
                encoding="utf-8",
            )
            out = root / "ci"

            result = self.run_cli("ci", "run", "--input", str(report), "--out", str(out))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            gate = json.loads((out / "gate_decision.json").read_text(encoding="utf-8"))
            severity = json.loads((out / "severity_decision.json").read_text(encoding="utf-8"))
            manifest = json.loads((out / "ci_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(gate["decision"], "pass")
            self.assertEqual(severity["severity"], "low")
            self.assertTrue(manifest["local_only"])
            self.assertEqual(manifest["external_api_call_count"], 0)
            self.assertEqual(manifest["raw_upload_count"], 0)
            self.assertTrue((out / "ci_summary.md").exists())
            self.assertTrue((out / "open_this_first_ci.md").exists())

    def test_ci_run_fails_gate_when_forbidden_or_private_markers_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "report"
            report.mkdir()
            (report / "diagnosis.json").write_text(
                json.dumps({"failure_type": "anti_bot_risk", "subtype": "fingerprint_risk"}),
                encoding="utf-8",
            )
            private_marker = "private" + "_solutions"
            unsafe_marker = "fingerprint " + "spoofing"
            (report / "unsafe.txt").write_text(
                f"{private_marker} marker and {unsafe_marker} guidance should block CI",
                encoding="utf-8",
            )
            out = root / "ci"

            result = self.run_cli("ci", "run", "--input", str(report), "--out", str(out))

            self.assertEqual(result.returncode, 3, result.stderr + result.stdout)
            gate = json.loads((out / "gate_decision.json").read_text(encoding="utf-8"))
            severity = json.loads((out / "severity_decision.json").read_text(encoding="utf-8"))
            self.assertEqual(gate["decision"], "fail")
            self.assertEqual(severity["severity"], "critical")
            self.assertGreaterEqual(severity["private_solution_leak_count"], 1)
            self.assertGreaterEqual(severity["forbidden_output_count"], 1)

    def test_ci_templates_generates_github_gitlab_jenkins_and_powershell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "templates"

            result = self.run_cli("ci", "templates", "--out", str(out))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            expected = [
                out / "github-actions" / "failure-doctor-ci.yml",
                out / "gitlab" / "failure-doctor-ci.yml",
                out / "jenkins" / "Jenkinsfile",
                out / "powershell" / "run_failure_doctor_ci.ps1",
            ]
            for path in expected:
                self.assertTrue(path.exists(), str(path))
                text = path.read_text(encoding="utf-8")
                self.assertIn("failure-doctor ci run", text)
                self.assertNotIn("upload-artifact", text.lower())

    def test_validation_runner_writes_pass_payload(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_ci_cd_integration_validation"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(
            (ROOT / "validation" / "ci_cd_integration_validation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 96)
        self.assertEqual(payload["forbidden_output_count"], 0)
        self.assertEqual(payload["private_solution_leak_count"], 0)
        self.assertEqual(payload["external_api_call_count"], 0)


if __name__ == "__main__":
    unittest.main()

