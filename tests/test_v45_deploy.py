from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import main


class DeployCliTests(unittest.TestCase):
    def test_backup_restore_and_offline_bundle_are_metadata_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "audit_log.jsonl").write_text('{"event":"created"}\n', encoding="utf-8")
            backup = root / "backup"
            restored = root / "restored"
            offline = root / "offline"
            self.assertEqual(main(["deploy", "backup", "--workspace", str(workspace), "--out", str(backup)]), 0)
            self.assertEqual(main(["deploy", "restore", "--backup", str(backup), "--out", str(restored)]), 0)
            self.assertEqual(main(["deploy", "offline-bundle", "--out", str(offline)]), 0)
            manifest = json.loads((offline / "offline_bundle_manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["contains_user_workspace_data"])
            self.assertEqual(manifest["private_content_found"], 0)

    def test_health_and_security_posture_are_local_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            health = root / "health"
            posture = root / "posture"
            self.assertEqual(main(["deploy", "health", "--workspace", str(workspace), "--out", str(health)]), 0)
            self.assertEqual(main(["deploy", "security-posture", "--workspace", str(workspace), "--out", str(posture)]), 0)
            payload = json.loads((posture / "security_posture_report.json").read_text(encoding="utf-8"))
            self.assertTrue(payload["local_only"])
            self.assertTrue(payload["no_upload"])


if __name__ == "__main__":
    unittest.main()
