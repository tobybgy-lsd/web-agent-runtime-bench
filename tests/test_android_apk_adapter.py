from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.android.diagnosis import diagnose_android_pack
from failure_doctor.android.flow import load_flow, validate_flow_file
from failure_doctor.android.safety import evaluate_flow_safety
from failure_doctor.android.ui_tree import parse_ui_tree_xml
from tools.validation.run_android_apk_automation_validation import build_validation_payload


class AndroidApkAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="afd-android-test-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ui_tree_normalizes_resource_text_and_bounds(self) -> None:
        xml = self.tmp / "ui.xml"
        xml.write_text(
            '<hierarchy><node resource-id="com.example:id/publish" text="Publish" '
            'content-desc="publish button" class="android.widget.Button" bounds="[10,20][110,70]" '
            'clickable="true" enabled="true" /></hierarchy>',
            encoding="utf-8",
        )
        tree = parse_ui_tree_xml(xml)
        self.assertEqual(tree["node_count"], 1)
        self.assertEqual(tree["nodes"][0]["resource_id"], "com.example:id/publish")
        self.assertEqual(tree["nodes"][0]["bounds"], {"x1": 10, "y1": 20, "x2": 110, "y2": 70})

    def test_flow_validation_blocks_final_submit_by_default(self) -> None:
        flow = {
            "schema_version": "android_flow/v1",
            "flow_id": "post_image_text_dry_run",
            "authorized_target": True,
            "target_kind": "mock_app",
            "package_name": "com.example.mock",
            "allow_final_submit": False,
            "steps": [{"id": "publish", "action": "tap", "final_submit": True, "locator": {"text": "Post"}}],
        }
        report = evaluate_flow_safety(flow)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("final_submit_requires_explicit_approval", report["blocked_reasons"])

    def test_flow_file_loads_and_validates_json_yaml_subset(self) -> None:
        path = self.tmp / "flow.yml"
        path.write_text(
            "\n".join(
                [
                    "schema_version: android_flow/v1",
                    "flow_id: safe_dry_run",
                    "authorized_target: true",
                    "target_kind: mock_app",
                    "package_name: com.example.mock",
                    "allow_final_submit: false",
                    "steps:",
                    "  - id: open_publish",
                    "    action: tap",
                    "    locator:",
                    "      resource_id: com.example:id/publish",
                ]
            ),
            encoding="utf-8",
        )
        flow = load_flow(path)
        self.assertEqual(flow["flow_id"], "safe_dry_run")
        validation = validate_flow_file(path)
        self.assertEqual(validation["status"], "pass")

    def test_diagnosis_detects_android_permission_dialog(self) -> None:
        pack = self.tmp / "pack"
        pack.mkdir()
        (pack / "logcat.txt").write_text("Permission Denial: camera permission dialog blocked upload", encoding="utf-8")
        diagnosis = diagnose_android_pack(pack)
        self.assertEqual(diagnosis["technical_category"], "anti_bot_risk")
        self.assertEqual(diagnosis["subtype"], "android_permission_dialog_blocked")

    def test_cli_android_help_and_validate_flow(self) -> None:
        flow = self.tmp / "flow.yml"
        flow.write_text(
            "\n".join(
                [
                    "schema_version: android_flow/v1",
                    "flow_id: cli_safe_dry_run",
                    "authorized_target: true",
                    "target_kind: mock_app",
                    "package_name: com.example.mock",
                    "allow_final_submit: false",
                    "steps:",
                    "  - id: open_publish",
                    "    action: tap",
                    "    locator:",
                    "      text: Publish",
                ]
            ),
            encoding="utf-8",
        )
        out = self.tmp / "out"
        proc = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "android", "validate-flow", str(flow), "--out", str(out)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout)
        payload = json.loads((out / "android_flow_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")

    def test_validation_payload_meets_v51_gate(self) -> None:
        payload = build_validation_payload()
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 180)
        self.assertEqual(payload["unsafe_flow_blocked"], payload["unsafe_flow_cases"])
        self.assertEqual(payload["forbidden_output_count"], 0)


if __name__ == "__main__":
    unittest.main()

