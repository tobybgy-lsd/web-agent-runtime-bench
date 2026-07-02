import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.ci.cli import handle_ci
from failure_doctor.cli import build_parser, main
from failure_doctor.console.server import create_console_app


class EnterpriseIntegrationTests(unittest.TestCase):
    def test_console_status_exposes_enterprise_mode_without_lan_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "enterprise"
            self.assertEqual(main(["enterprise", "init", "--workspace", str(workspace)]), 0)
            app = create_console_app(workspace=Path(tmp) / "console", enterprise=True, enterprise_workspace=workspace)
            status_code, _headers, body = app._handle_get("/api/status", "")
            self.assertEqual(status_code, 200)
            status = json.loads(body.decode("utf-8"))
            self.assertEqual(status["enterprise"]["enabled"], True)
            self.assertEqual(status["enterprise"]["auth"], "local")
            self.assertEqual(status["enterprise"]["allow_lan"], False)
            self.assertEqual(status["enterprise"]["external_api_call_count"], 0)

    def test_ci_diagnose_attaches_enterprise_audit_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "enterprise"
            project = root / "project"
            out = root / "ci"
            project.mkdir()
            (project / "error.log").write_text("Timeout waiting for selector", encoding="utf-8")
            self.assertEqual(main(["enterprise", "init", "--workspace", str(workspace)]), 0)

            parser = build_parser()
            args = parser.parse_args(
                [
                    "ci",
                    "diagnose",
                    "--project",
                    str(project),
                    "--out",
                    str(out),
                    "--enterprise-workspace",
                    str(workspace),
                ]
            )
            self.assertEqual(handle_ci(args), 0)
            summary = json.loads((out / "enterprise_ci_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["enterprise_policy"], "active")
            self.assertTrue(summary["enterprise_audit_ref"].startswith("audit_"))


if __name__ == "__main__":
    unittest.main()
