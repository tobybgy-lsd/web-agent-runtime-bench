import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import main


class EnterpriseCliTests(unittest.TestCase):
    def test_enterprise_workspace_user_policy_audit_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / ".failure-doctor-enterprise"
            audit_out = root / "audit_export"

            self.assertEqual(main(["enterprise", "init", "--workspace", str(workspace)]), 0)
            self.assertTrue((workspace / "enterprise_manifest.json").exists())
            self.assertTrue((workspace / "audit" / "audit_log.jsonl").exists())

            self.assertEqual(
                main(
                    [
                        "enterprise",
                        "user",
                        "add",
                        "--workspace",
                        str(workspace),
                        "--username",
                        "alice",
                        "--role",
                        "developer",
                    ]
                ),
                0,
            )
            users = json.loads((workspace / "users.json").read_text(encoding="utf-8"))
            self.assertEqual(users["users"]["alice"]["role"], "developer")

            self.assertEqual(main(["enterprise", "role", "list", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["enterprise", "policy", "list", "--workspace", str(workspace)]), 0)

            self.assertEqual(
                main(
                    [
                        "enterprise",
                        "request",
                        "handoff",
                        "--workspace",
                        str(workspace),
                        "--report",
                        str(root),
                        "--target",
                        "codex",
                    ]
                ),
                0,
            )
            pending = sorted((workspace / "approvals" / "pending").glob("*.json"))
            self.assertTrue(pending)
            request_id = json.loads(pending[0].read_text(encoding="utf-8"))["request_id"]

            self.assertEqual(
                main(
                    [
                        "enterprise",
                        "approve",
                        "--workspace",
                        str(workspace),
                        "--request-id",
                        request_id,
                        "--decision",
                        "approve",
                    ]
                ),
                0,
            )
            self.assertTrue((workspace / "approvals" / "approved" / f"{request_id}.json").exists())

            self.assertEqual(main(["enterprise", "validate", "--workspace", str(workspace)]), 0)
            self.assertEqual(
                main(
                    [
                        "enterprise",
                        "audit",
                        "export",
                        "--workspace",
                        str(workspace),
                        "--out",
                        str(audit_out),
                        "--sanitized-only",
                    ]
                ),
                0,
            )
            exported = json.loads((audit_out / "audit_export.json").read_text(encoding="utf-8"))
            self.assertEqual(exported["sanitized_only"], True)
            self.assertGreaterEqual(exported["event_count"], 4)


if __name__ == "__main__":
    unittest.main()
