from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.console.server import create_console_app


class HybridReasoningIntegrationTests(unittest.TestCase):
    def test_ci_diagnose_can_attach_hybrid_reasoning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            (project / "error.log").write_text("net::ERR_PROXY_CONNECTION_FAILED\n", encoding="utf-8")
            out = root / "ci"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "ci",
                    "diagnose",
                    "--project",
                    str(project),
                    "--out",
                    str(out),
                    "--hybrid-reasoning",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((out / "hybrid_reasoning" / "hybrid_reasoning_report.json").exists())
            self.assertIn("Hybrid Reasoning", (out / "ci_summary.md").read_text(encoding="utf-8"))

    def test_console_exposes_hybrid_reasoning_status_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = create_console_app(
                workspace=Path(tmp),
                host="127.0.0.1",
                port=8765,
                enable_hybrid_reasoning=True,
                reasoner="mock_reasoner",
            )

            status, _headers, body = app.handle("GET", "/api/status", {}, b"")
            payload = json.loads(body.decode("utf-8"))
            self.assertEqual(status, 200)
            self.assertEqual(payload["hybrid_reasoning"]["enabled"], True)
            self.assertEqual(payload["hybrid_reasoning"]["reasoner"], "mock_reasoner")

            status, _headers, body = app.handle("GET", "/api/reasoning/status", {}, b"")
            payload = json.loads(body.decode("utf-8"))
            self.assertEqual(status, 200)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["enabled"], True)


if __name__ == "__main__":
    unittest.main()

