import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import build_artifact, collect_inputs, enrich_for_users
from tools.failure_artifacts.diagnose import diagnose_artifact


class FailureDoctorPublicLogRuleTests(unittest.TestCase):
    def diagnose_log(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "error.log"
            log.write_text(text, encoding="utf-8")
            evidence = collect_inputs(log)
            artifact = build_artifact(evidence, run_id="public_log_rule")
            diagnosis = diagnose_artifact(artifact)
            public = enrich_for_users(diagnosis)
            return {**public, "raw": diagnosis}

    def test_proxy_connection_failed_maps_to_network_problem(self):
        result = self.diagnose_log("page.goto: net::ERR_PROXY_CONNECTION_FAILED at https://example.test")
        self.assertEqual(result["technical_category"], "network_http_error")
        self.assertEqual(result["subtype"], "proxy_connection_failed")
        self.assertEqual(result["user_facing_category"], "网络/代理问题")

    def test_dns_name_not_resolved_maps_to_network_problem(self):
        result = self.diagnose_log("Error: page.goto: net::ERR_NAME_NOT_RESOLVED at https://internal.invalid")
        self.assertEqual(result["technical_category"], "network_http_error")
        self.assertEqual(result["subtype"], "dns_name_not_resolved")
        self.assertEqual(result["user_facing_category"], "网络/代理问题")

    def test_tls_certificate_error_maps_to_network_problem(self):
        result = self.diagnose_log("page.goto: net::ERR_CERT_AUTHORITY_INVALID while opening staging")
        self.assertEqual(result["technical_category"], "network_http_error")
        self.assertEqual(result["subtype"], "tls_certificate_error")

    def test_strict_mode_violation_maps_to_element_problem(self):
        result = self.diagnose_log("locator.click: Error: strict mode violation: locator('button') resolved to 2 elements")
        self.assertEqual(result["technical_category"], "playwright_strict_mode_violation")
        self.assertEqual(result["subtype"], "locator_multiple_matches")
        self.assertEqual(result["user_facing_category"], "按钮/元素找不到")

    def test_target_closed_maps_to_browser_environment(self):
        result = self.diagnose_log("locator.click: Target page, context or browser has been closed")
        self.assertEqual(result["technical_category"], "playwright_browser_context_closed")
        self.assertEqual(result["subtype"], "target_closed")
        self.assertEqual(result["user_facing_category"], "浏览器环境不一致")

    def test_execution_context_destroyed_maps_to_waiting_logic(self):
        result = self.diagnose_log("Error: Execution context was destroyed, most likely because of a navigation")
        self.assertEqual(result["technical_category"], "playwright_execution_context_destroyed")
        self.assertEqual(result["subtype"], "navigation_race")
        self.assertEqual(result["user_facing_category"], "页面没加载完")

    def test_navigation_timeout_maps_to_page_not_loaded(self):
        result = self.diagnose_log("TimeoutError: page.goto: Timeout 30000ms exceeded waiting until load")
        self.assertEqual(result["technical_category"], "async_hydration_timing")
        self.assertEqual(result["user_facing_category"], "页面没加载完")

    def test_download_not_saved_maps_to_upload_download_failure(self):
        result = self.diagnose_log("Download event fired but file was not saved; acceptDownloads is false")
        self.assertEqual(result["technical_category"], "playwright_download")
        self.assertEqual(result["subtype"], "download_event")
        self.assertEqual(result["user_facing_category"], "文件上传下载失败")

    def test_cdp_websocket_disconnect_maps_to_browser_environment(self):
        result = self.diagnose_log("CDP WebSocket silent disconnect: httpx.ReadError while browser session is alive")
        self.assertEqual(result["technical_category"], "cdp_websocket_disconnected")
        self.assertEqual(result["subtype"], "websocket_disconnect")
        self.assertEqual(result["user_facing_category"], "浏览器环境不一致")

    def test_agent_repetition_loop_maps_to_waiting_logic(self):
        result = self.diagnose_log("Agent repeatedly executed extract_content action in an infinite loop")
        self.assertEqual(result["technical_category"], "agent_repetition_loop")
        self.assertEqual(result["subtype"], "repeated_action_loop")
        self.assertEqual(result["user_facing_category"], "代码等待逻辑错误")


if __name__ == "__main__":
    unittest.main()
