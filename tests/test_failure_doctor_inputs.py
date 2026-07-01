import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import build_artifact, collect_inputs, enrich_for_users, input_summary_for, user_category_for
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
        self.assertEqual(user_category_for("website_change"), "网站结构变化")
        self.assertEqual(user_category_for("anti_bot_risk"), "疑似风控/访问限制")

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

    def test_user_supplied_probe_report_is_offline_transport_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "probe_report.json").write_text(
                json.dumps(
                    {
                        "schema_version": "failure-doctor/probe-report/v1",
                        "network_access": "performed_by_user_before_diagnosis",
                        "transport": {
                            "tls_alpn_fingerprint_mismatch": True,
                            "alpn": "http/1.1",
                            "browser_alpn": "h2",
                            "http_version": "1.1",
                            "browser_http_version": "2",
                        },
                        "ip_reputation": {"classification": "uncertain"},
                    }
                ),
                encoding="utf-8",
            )

            evidence = collect_inputs(root)
            summary = input_summary_for(evidence)
            artifact = build_artifact(evidence, run_id="probe_report")
            diagnosis = classify_failure_artifact(artifact)

            self.assertEqual(summary["observed_evidence"]["probe_reports"], 1)
            self.assertEqual(summary["evidence_priority"], ["probe_report"])
            self.assertIn("probe_report.json", summary["recognized_files"]["probe_reports"])
            self.assertFalse(artifact["safety"]["external_network_required"])
            self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
            self.assertEqual(diagnosis["subtype"], "tls_alpn_fingerprint_mismatch")

    def test_user_supplied_browser_runtime_report_is_offline_behavioral_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "browser_runtime_report.json").write_text(
                json.dumps(
                    {
                        "schema_version": "failure-doctor/browser-runtime-report/v1",
                        "network_access": "none",
                        "browser_runtime": {
                            "client_hints_platform_mismatch": True,
                            "user_agent_platform": "macOS",
                            "sec_ch_ua_platform": "Windows",
                            "navigator_platform": "Win32",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (root / "input_timing_summary.json").write_text(
                json.dumps(
                    {
                        "schema_version": "failure-doctor/input-timing-summary/v1",
                        "network_access": "none",
                        "input_timing": {
                            "zero_interval_input_detected": True,
                            "fixed_interval_input_detected": True,
                            "average_key_interval_ms": 0,
                            "interval_variance_ms2": 0,
                            "input_method": "bulk_fill",
                        },
                    }
                ),
                encoding="utf-8",
            )

            evidence = collect_inputs(root)
            summary = input_summary_for(evidence)
            artifact = build_artifact(evidence, run_id="browser_runtime_report")
            diagnosis = classify_failure_artifact(artifact)

            self.assertEqual(summary["observed_evidence"]["runtime_reports"], 2)
            self.assertIn("browser_runtime_report.json", summary["recognized_files"]["runtime_reports"])
            self.assertIn("input_timing_summary.json", summary["recognized_files"]["runtime_reports"])
            self.assertFalse(artifact["safety"]["external_network_required"])
            self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
            self.assertEqual(diagnosis["subtype"], "client_hints_platform_mismatch")

    def test_user_supplied_canvas_runtime_report_is_offline_fingerprint_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "browser_runtime_report.json").write_text(
                json.dumps(
                    {
                        "schema_version": "failure-doctor/browser-runtime-report/v1",
                        "network_access": "none",
                        "browser_runtime": {
                            "canvas_fingerprint_collision": True,
                            "duplicate_canvas_hash_count": 3,
                            "total_sessions": 5,
                            "evidence_source": "sanitized-authorized-test",
                        },
                    }
                ),
                encoding="utf-8",
            )

            evidence = collect_inputs(root)
            summary = input_summary_for(evidence)
            artifact = build_artifact(evidence, run_id="canvas_runtime_report")
            diagnosis = classify_failure_artifact(artifact)

            self.assertEqual(summary["observed_evidence"]["runtime_reports"], 1)
            self.assertEqual(summary["evidence_priority"], ["runtime_report"])
            self.assertIn("browser_runtime_report.json", summary["recognized_files"]["runtime_reports"])
            self.assertFalse(artifact["safety"]["external_network_required"])
            self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
            self.assertEqual(diagnosis["subtype"], "canvas_fingerprint_collision")

    def test_user_supplied_js_integrity_report_is_offline_script_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "js_integrity_report.json").write_text(
                json.dumps(
                    {
                        "schema_version": "failure-doctor/js-integrity-report/v1",
                        "network_access": "none",
                        "script_integrity": {
                            "js_ast_obfuscation_detected": True,
                            "rotated_string_array_detected": True,
                            "client_generated_token_missing": True,
                            "request_integrity_algorithm_changed": False,
                        },
                    }
                ),
                encoding="utf-8",
            )

            evidence = collect_inputs(root)
            summary = input_summary_for(evidence)
            artifact = build_artifact(evidence, run_id="js_integrity_report")
            diagnosis = classify_failure_artifact(artifact)

            self.assertEqual(summary["observed_evidence"]["script_reports"], 1)
            self.assertEqual(summary["evidence_priority"], ["script_report"])
            self.assertIn("js_integrity_report.json", summary["recognized_files"]["script_reports"])
            self.assertFalse(artifact["safety"]["external_network_required"])
            self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
            self.assertEqual(diagnosis["subtype"], "js_ast_obfuscation_detected")

    def test_user_supplied_deep_runtime_report_maps_webgl_webrtc_and_sandbox_evidence(self):
        cases = {
            "webgl_virtual_renderer_detected": {
                "browser_runtime": {
                    "webgl_virtual_renderer_detected": True,
                    "webgl_renderer_family": "virtualized",
                    "evidence_source": "sanitized-authorized-test",
                }
            },
            "webrtc_private_ip_leak_detected": {
                "browser_runtime": {
                    "webrtc_private_ip_leak_detected": True,
                    "ice_candidate_summary": "private-range-candidate-present",
                    "evidence_source": "sanitized-authorized-test",
                }
            },
            "automation_global_scope_leak_detected": {
                "browser_runtime": {
                    "automation_global_scope_leak_detected": True,
                    "global_scope_summary": "automation-globals-present",
                    "evidence_source": "sanitized-authorized-test",
                }
            },
            "runtime_sandbox_leak_detected": {
                "browser_runtime": {
                    "runtime_sandbox_leak_detected": True,
                    "sandbox_summary": "server-runtime-global-present",
                    "evidence_source": "sanitized-authorized-test",
                }
            },
            "native_function_integrity_mismatch": {
                "browser_runtime": {
                    "native_function_integrity_mismatch": True,
                    "native_reflection_summary": "browser-native-reflection-mismatch",
                    "evidence_source": "sanitized-authorized-test",
                }
            },
            "debugger_timing_anomaly": {
                "browser_runtime": {
                    "debugger_timing_anomaly": True,
                    "debugger_timing_bucket": "threshold-exceeded",
                    "evidence_source": "sanitized-authorized-test",
                }
            },
        }
        for expected_subtype, report in cases.items():
            with self.subTest(expected_subtype=expected_subtype):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / "browser_runtime_report.json").write_text(
                        json.dumps(
                            {
                                "schema_version": "failure-doctor/browser-runtime-report/v1",
                                "network_access": "none",
                                **report,
                            }
                        ),
                        encoding="utf-8",
                    )

                    artifact = build_artifact(collect_inputs(root), run_id=expected_subtype)
                    diagnosis = classify_failure_artifact(artifact)

                    self.assertFalse(artifact["safety"]["external_network_required"])
                    self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
                    self.assertEqual(diagnosis["subtype"], expected_subtype)

    def test_user_supplied_protocol_report_maps_http2_and_ja4_evidence(self):
        cases = {
            "http2_settings_fingerprint_mismatch": {
                "transport": {
                    "http2_settings_fingerprint_mismatch": True,
                    "http2_settings_summary": "settings-family-differs",
                    "alpn": "h2",
                }
            },
            "ja4_h2_fingerprint_mismatch": {
                "transport": {
                    "ja4_h2_fingerprint_mismatch": True,
                    "ja4_h2_summary": "browser-protocol-stack-differs",
                    "alpn": "h2",
                }
            },
        }
        for expected_subtype, report in cases.items():
            with self.subTest(expected_subtype=expected_subtype):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / "probe_report.json").write_text(
                        json.dumps(
                            {
                                "schema_version": "failure-doctor/probe-report/v1",
                                "network_access": "performed_by_user_before_diagnosis",
                                **report,
                            }
                        ),
                        encoding="utf-8",
                    )

                    artifact = build_artifact(collect_inputs(root), run_id=expected_subtype)
                    diagnosis = classify_failure_artifact(artifact)

                    self.assertFalse(artifact["safety"]["external_network_required"])
                    self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
                    self.assertEqual(diagnosis["subtype"], expected_subtype)

    def test_user_supplied_behavior_and_vm_reports_map_precise_evidence(self):
        cases = {
            "pointer_trajectory_entropy_anomaly": (
                "input_timing_summary.json",
                {
                    "input_timing": {
                        "pointer_trajectory_entropy_anomaly": True,
                        "vertical_deviation_bucket": "too-low",
                        "evidence_source": "sanitized-authorized-test",
                    }
                },
            ),
            "mathematical_trajectory_detected": (
                "input_timing_summary.json",
                {
                    "input_timing": {
                        "mathematical_trajectory_detected": True,
                        "acceleration_profile": "too-deterministic",
                        "evidence_source": "sanitized-authorized-test",
                    }
                },
            ),
            "js_vmp_integrity_check_failed": (
                "js_integrity_report.json",
                {
                    "script_integrity": {
                        "js_vmp_integrity_check_failed": True,
                        "client_vm_summary": "signature-mismatch",
                        "evidence_source": "sanitized-authorized-test",
                    }
                },
            ),
            "numeric_semantics_mismatch": (
                "js_integrity_report.json",
                {
                    "script_integrity": {
                        "numeric_semantics_mismatch": True,
                        "numeric_semantics_summary": "runtime-arithmetic-differs",
                        "evidence_source": "sanitized-authorized-test",
                    }
                },
            ),
        }
        for expected_subtype, (filename, report) in cases.items():
            with self.subTest(expected_subtype=expected_subtype):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / filename).write_text(
                        json.dumps({"schema_version": "failure-doctor/offline-report/v1", "network_access": "none", **report}),
                        encoding="utf-8",
                    )

                    artifact = build_artifact(collect_inputs(root), run_id=expected_subtype)
                    diagnosis = classify_failure_artifact(artifact)

                    self.assertFalse(artifact["safety"]["external_network_required"])
                    self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
                    self.assertEqual(diagnosis["subtype"], expected_subtype)

    def test_error_log_outranks_large_console_html_for_diagnosis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            noisy_html = (
                "<html><body><form><input name='username'></form>"
                "<a href='/challenge/scraping-random-pagination/2fe6286a4e5f'>next</a>"
                + ("<div>pagination content</div>" * 80)
                + "</body></html>"
            )
            (root / "console.txt").write_text(noisy_html, encoding="utf-8")
            (root / "error.log").write_text(
                "FileNotFoundError: [Errno 2] No such file or directory: './data/e03/e03_1.html'",
                encoding="utf-8",
            )

            artifact = build_artifact(collect_inputs(root), run_id="error_priority")
            diagnosis = classify_failure_artifact(artifact)

            self.assertIn("FileNotFoundError", artifact["error"]["message"])
            self.assertEqual(diagnosis["failure_type"], "toolchain_environment")

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

        self.assertEqual(public["user_facing_category"], "疑似风控/访问限制")
        self.assertEqual(public["technical_category"], "anti_bot_risk")
        self.assertEqual(public["failure_layer"], "anti_bot_risk")
        self.assertIn("codex_fix_prompt.md", public["next_action"])
        self.assertIn(public["estimated_fix_difficulty"], {"easy", "medium", "hard"})
        self.assertTrue(public["confidence_reason"])


if __name__ == "__main__":
    unittest.main()
