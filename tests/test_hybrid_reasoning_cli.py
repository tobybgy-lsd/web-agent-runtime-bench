from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class HybridReasoningCliTests(unittest.TestCase):
    def test_reason_command_writes_evidence_bound_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "report"
            report.mkdir()
            (report / "diagnosis.json").write_text(
                json.dumps(
                    {
                        "user_facing_category": "Network or proxy issue",
                        "technical_category": "network_http_error",
                        "subtype": "proxy_connection_failed",
                        "confidence": 0.86,
                        "next_action": "Check local proxy configuration and retry with sanitized evidence.",
                    }
                ),
                encoding="utf-8",
            )
            out = root / "reasoning"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "reason",
                    "--input",
                    str(report),
                    "--out",
                    str(out),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads((out / "hybrid_reasoning_report.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["reasoning_status"], "validated")
            self.assertEqual(payload["provider"], "mock_reasoner")
            self.assertTrue(payload["claims"])
            self.assertTrue(payload["claims"][0]["supporting_evidence_ids"])

    def test_diagnose_can_attach_hybrid_reasoning_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            failed = root / "failed"
            failed.mkdir()
            (failed / "error.log").write_text("net::ERR_PROXY_CONNECTION_FAILED\n", encoding="utf-8")
            out = root / "report"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "diagnose",
                    str(failed),
                    "--out",
                    str(out),
                    "--hybrid-reasoning",
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((out / "hybrid_reasoning" / "hybrid_reasoning_report.json").exists())
            self.assertTrue((out / "hybrid_reasoning_summary.md").exists())

    def test_agent_bootstrap_includes_hybrid_reasoning_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "agent-bootstrap",
                    "--target",
                    "codex",
                    "--project",
                    str(project),
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            target = project / ".failure-doctor" / "agents" / "codex"
            self.assertTrue((target / "hybrid_reasoning_workflow.md").exists())
            manifest = json.loads(
                (project / ".failure-doctor" / "agents" / "agent_invocation_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn("hybrid_reasoning_command", manifest)


if __name__ == "__main__":
    unittest.main()
