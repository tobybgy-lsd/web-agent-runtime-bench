from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import main
from tools.validation.run_android_authoring_validation import build_validation_payload as authoring_payload
from tools.validation.run_android_pilot_validation import build_validation_payload as pilot_payload
from tools.validation.run_android_deep_diagnostics_validation import build_validation_payload as dx_payload
from tools.validation.run_android_playbook_validation import build_validation_payload as playbook_payload
from tools.validation.run_real_apk_pilot_program_validation import build_validation_payload as real_pilot_payload
from tools.validation.run_android_device_lab_hardening_validation import build_validation_payload as lab_payload
from tools.validation.run_mobile_automation_stability_validation import build_validation_payload as stability_payload


class AndroidMobileStableCLITest(unittest.TestCase):
    def test_new_command_groups_help(self) -> None:
        for command in [
            "android-author",
            "android-pilot",
            "android-dx",
            "android-playbook",
            "android-real-pilot",
            "android-lab",
            "mobile-stability",
        ]:
            with self.subTest(command=command):
                with self.assertRaises(SystemExit) as ctx:
                    main([command, "--help"])
                self.assertEqual(ctx.exception.code, 0)

    def test_authoring_pilot_dx_smoke_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(main(["android-author", "flow", "draft", "--recording", str(root), "--out", str(root / "draft")]), 0)
            self.assertTrue((root / "draft" / "flow.yml").exists())
            self.assertEqual(main(["android-pilot", "project-init", "--name", "mock_company_app", "--out", str(root / "pilot")]), 0)
            self.assertTrue((root / "pilot" / "pilot_manifest.json").exists())
            self.assertEqual(main(["android-dx", "bundle-create", "--run", str(root / "run"), "--out", str(root / "bundle")]), 0)
            self.assertTrue((root / "bundle" / "bundle_manifest.json").exists())

    def test_later_stage_smoke_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(main(["android-playbook", "list"]), 0)
            self.assertEqual(main(["android-real-pilot", "init", "--out", str(root / "real")]), 0)
            self.assertEqual(main(["android-lab", "init", "--out", str(root / "lab")]), 0)
            self.assertEqual(main(["mobile-stability", "check-android-cli", "--out", str(root / "stable")]), 0)

    def test_validation_payloads_pass_and_are_safe(self) -> None:
        for payload in [
            authoring_payload(), pilot_payload(), dx_payload(), playbook_payload(),
            real_pilot_payload(), lab_payload(), stability_payload(),
        ]:
            with self.subTest(version=payload["version"]):
                self.assertEqual(payload["status"], "pass")
                self.assertGreaterEqual(payload["total_cases"], 230)
                self.assertEqual(payload["forbidden_output_count"], 0)
                self.assertEqual(payload["private_solution_leak_count"], 0)
                self.assertEqual(payload["real_platform_access_count"], 0)
                self.assertEqual(payload["external_api_call_count"], 0)


if __name__ == "__main__":
    unittest.main()


