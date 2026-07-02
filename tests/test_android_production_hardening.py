from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.android_pro.app_profile import create_app_profile, validate_app_profile
from failure_doctor.android_pro.flow_linter import lint_flow_file
from failure_doctor.android_pro.locator_registry import build_locator_registry, validate_locator_registry
from failure_doctor.android_pro.locator_self_healing import recommend_locator_heal
from failure_doctor.android_pro.publish_guard import evaluate_publish_guard
from failure_doctor.android_pro.ui_tree_diff import diff_ui_trees


ROOT = Path(__file__).resolve().parents[1]


class AndroidProductionHardeningTests(unittest.TestCase):
    def test_profile_init_validate_and_cli_help(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "profile"
            profile = create_app_profile("com.example.mockapp", out)
            self.assertTrue((out / "android_app_profile.json").exists())
            self.assertTrue(profile["authorized_target"])
            self.assertFalse(profile["allow_final_submit_default"])
            self.assertEqual(validate_app_profile(out)["status"], "pass")

        result = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "android-pro", "--help"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("profile", result.stdout)

    def test_locator_registry_blocks_absolute_coordinate_primary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            registry_dir = Path(td) / "registry"
            registry = {
                "schema_version": "android_locator_registry/v1",
                "profile_id": "demo",
                "pages": {
                    "publish_page": {
                        "submit_button": {
                            "primary": {"strategy": "coordinate", "value": "100,200"},
                            "fallbacks": [],
                            "risk_level": "high",
                        }
                    }
                },
            }
            registry_dir.mkdir()
            (registry_dir / "android_locator_registry.json").write_text(json.dumps(registry), encoding="utf-8")
            report = validate_locator_registry(registry_dir)
            self.assertEqual(report["status"], "fail")
            self.assertIn("absolute_coordinate_primary", report["findings"][0]["code"])

    def test_page_object_registry_diff_and_heal_are_recommendation_only(self) -> None:
        old_ui = """<hierarchy><node resource-id="app:id/title" text="" class="android.widget.EditText" bounds="[0,0][100,40]" /><node resource-id="app:id/save" text="Save" content-desc="Save draft" class="android.widget.Button" bounds="[0,50][100,90]" /></hierarchy>"""
        new_ui = """<hierarchy><node resource-id="app:id/title_new" text="" class="android.widget.EditText" bounds="[0,0][100,40]" /><node resource-id="app:id/save" text="Save draft" content-desc="Save draft" class="android.widget.Button" bounds="[0,50][100,90]" /></hierarchy>"""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            old = td_path / "old.xml"
            new = td_path / "new.xml"
            old.write_text(old_ui, encoding="utf-8")
            new.write_text(new_ui, encoding="utf-8")
            registry = build_locator_registry(old, td_path / "registry")
            self.assertEqual(registry["status"], "pass")
            diff = diff_ui_trees(old, new, td_path / "diff")
            self.assertGreaterEqual(len(diff["changes"]), 1)
            failed = td_path / "failed_locator.json"
            failed.write_text(json.dumps({"strategy": "resource_id", "value": "app:id/title"}), encoding="utf-8")
            heal = recommend_locator_heal(old, new, failed, td_path / "heal")
            self.assertFalse(heal["auto_apply_allowed"])
            self.assertTrue(heal["candidates"])
            self.assertTrue(heal["candidates"][0]["requires_manual_approval"])

    def test_flow_linter_and_publish_guard_block_unsafe_final_submit(self) -> None:
        unsafe_flow = """schema_version: android_flow/v1
authorized_target: true
target_kind: mock_app
allow_final_submit: true
steps:
  - action: tap
    text: 发布
"""
        with tempfile.TemporaryDirectory() as td:
            flow = Path(td) / "flow.yml"
            flow.write_text(unsafe_flow, encoding="utf-8")
            lint = lint_flow_file(flow, None, Path(td) / "lint")
            self.assertEqual(lint["status"], "fail")
            self.assertTrue(any(item["severity"] == "critical" for item in lint["findings"]))
            guard = evaluate_publish_guard({"text": "发布", "allow_final_submit": False}, Path(td) / "guard")
            self.assertEqual(guard["decision"], "blocked")


if __name__ == "__main__":
    unittest.main()
