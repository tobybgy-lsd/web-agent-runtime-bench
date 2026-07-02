from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.console.server import create_console_app


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "failure_doctor", *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_report(root: Path, name: str) -> Path:
    report = root / name
    report.mkdir(parents=True)
    diagnosis = {
        "failure_type": "network_proxy",
        "technical_category": "network_proxy",
        "subtype": "proxy_connection_failed",
        "confidence": 0.84,
        "next_action": "Check authorized proxy configuration.",
        "raw_diagnosis": {
            "failure_type": "network_proxy",
            "subtype": "proxy_connection_failed",
            "observations": {"error_signature": "ERR_PROXY_CONNECTION_FAILED"},
        },
    }
    (report / "diagnosis.json").write_text(json.dumps(diagnosis, indent=2), encoding="utf-8")
    (report / "diagnosis.md").write_text("# Diagnosis\n\nERR_PROXY_CONNECTION_FAILED\n", encoding="utf-8")
    return report


class LocalFailureKbIntegrationTests(unittest.TestCase):
    def test_ci_diagnose_with_kb_adds_historical_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "kb"
            report = write_report(root, "report")
            ci_out = root / "ci"
            self.assertEqual(run_cli("kb", "init", "--path", str(kb)).returncode, 0)
            self.assertEqual(run_cli("kb", "import-report", "--kb", str(kb), "--report", str(report)).returncode, 0)

            result = run_cli("ci", "diagnose", "--project", str(report), "--kb", str(kb), "--out", str(ci_out))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((ci_out / "similar_cases.json").exists())
            self.assertIn("Similar Historical Cases", (ci_out / "ci_summary.md").read_text(encoding="utf-8"))

    def test_console_can_read_kb_without_raw_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "kb"
            report = write_report(root, "report")
            self.assertEqual(run_cli("kb", "init", "--path", str(kb)).returncode, 0)
            self.assertEqual(run_cli("kb", "import-report", "--kb", str(kb), "--report", str(report)).returncode, 0)
            app = create_console_app(workspace=root / "console", kb=kb)

            status, _headers, body = app.handle("GET", "/api/kb/cases", {}, b"")
            self.assertEqual(status, 200)
            payload = json.loads(body.decode("utf-8"))
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(len(payload["cases"]), 1)
            self.assertNotIn("diagnosis_summary", payload["cases"][0])

    def test_agent_bootstrap_writes_knowledge_base_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_cli("agent-bootstrap", "--target", "codex", "--project", str(root))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            workflow = root / ".failure-doctor" / "agents" / "codex" / "knowledge_base_workflow.md"
            self.assertTrue(workflow.exists())
            text = workflow.read_text(encoding="utf-8")
            self.assertIn("similar_cases.md", text)
            self.assertIn("Do not blindly apply old fixes", text)


if __name__ == "__main__":
    unittest.main()

