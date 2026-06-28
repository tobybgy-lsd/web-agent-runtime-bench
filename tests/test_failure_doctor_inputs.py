import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import collect_inputs, enrich_for_users, user_category_for
from tools.failure_artifacts.classifier import classify_failure_artifact


class FailureDoctorInputTests(unittest.TestCase):
    def test_user_category_mapping_covers_public_categories(self):
        self.assertEqual(user_category_for("playwright_storage_state_context"), "登录状态失效")
        self.assertEqual(user_category_for("selector_drift"), "按钮/元素找不到")
        self.assertEqual(user_category_for("async_hydration_timing"), "页面没加载完")
        self.assertEqual(user_category_for("playwright_popup"), "弹窗/遮罩挡住")
        self.assertEqual(user_category_for("response_shape_change"), "接口返回变了")
        self.assertEqual(user_category_for("rate_limit_or_soft_block"), "请求被限流")
        self.assertEqual(user_category_for("network_http_error"), "网络/代理问题")
        self.assertEqual(user_category_for("runtime_api_missing"), "浏览器环境不一致")

    def test_collect_inputs_detects_network_json_description_and_screenshot_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "network.json").write_text(json.dumps([{"url": "https://example.test", "status": 429}]), encoding="utf-8")
            (root / "user_description.txt").write_text("AI automation was rate limited.", encoding="utf-8")
            (root / "screenshot.jpg").write_bytes(b"fakejpg")

            evidence = collect_inputs(root)

            self.assertEqual(evidence["network_events"][0]["status"], 429)
            self.assertIn("rate limited", evidence["descriptions"][0]["text"])
            self.assertEqual(evidence["screenshot_metadata"][0]["image_understanding"], "metadata_only")

    def test_enrich_for_users_preserves_raw_diagnosis_fields(self):
        artifact = {
            "schema_version": "failure-artifact/v1",
            "run_id": "rate_limit_log",
            "tool": "agent_failure_doctor",
            "target_type": "sanitized_real_failure",
            "summary": "Rate limited request",
            "error": {"message": "HTTP 429 too many requests", "stack": "", "status_code": 429},
            "artifacts": {},
            "observations": {"log_excerpt": "HTTP 429 too many requests"},
            "expected": {"required_fields": []},
            "actual": {"fields": {}, "array_length": None},
            "labels": {"failure_type": "unknown", "confidence": 0.0},
            "safety": {
                "sanitized": True,
                "contains_credentials": False,
                "external_network_required": False,
                "user_authorized_or_synthetic": True,
            },
        }
        diagnosis = classify_failure_artifact(artifact)
        public = enrich_for_users(diagnosis)

        self.assertEqual(public["user_facing_category"], "请求被限流")
        self.assertEqual(public["technical_category"], "rate_limit_or_soft_block")
        self.assertIn("codex_fix_prompt.md", public["next_action"])
        self.assertIn(public["estimated_fix_difficulty"], {"easy", "medium", "hard"})
        self.assertTrue(public["confidence_reason"])


if __name__ == "__main__":
    unittest.main()
