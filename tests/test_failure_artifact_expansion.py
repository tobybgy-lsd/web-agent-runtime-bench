import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.failure_artifacts.adapters import artifact_from_playwright_trace, artifact_from_requests_run, artifact_from_scrapy_run
from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.regression import generate_synthetic_fixture


class FailureArtifactExpansionTests(unittest.TestCase):
    def test_classifier_detects_selector_drift(self):
        artifact = {
            "schema_version": "failure-artifact/v1",
            "run_id": "selector_001",
            "tool": "playwright",
            "target_type": "sanitized_real_failure",
            "summary": "Selector timeout after DOM changed",
            "error": {"message": "Timeout 30000ms waiting for selector .price", "status_code": 200},
            "artifacts": {"html_snapshot": "snapshot.html"},
            "observations": {"missing_selectors": [".price"], "dom_contains_text": ["amount"]},
            "expected": {"required_fields": ["title", "price"]},
            "actual": {"fields": {"title": "Demo"}, "array_length": None},
            "labels": {"failure_type": "unknown", "confidence": 0.0},
            "safety": {
                "sanitized": True,
                "contains_credentials": False,
                "external_network_required": False,
                "user_authorized_or_synthetic": True,
            },
        }

        diagnosis = classify_failure_artifact(artifact)

        self.assertEqual(diagnosis["failure_type"], "selector_drift")
        self.assertGreaterEqual(diagnosis["confidence"], 0.8)

    def test_classifier_detects_async_hydration_timing(self):
        artifact = {
            "schema_version": "failure-artifact/v1",
            "run_id": "timing_001",
            "tool": "playwright",
            "target_type": "sanitized_real_failure",
            "summary": "Hydration completed after extraction",
            "error": {"message": "locator('.product-card') resolved to 0 elements before hydration", "status_code": 200},
            "artifacts": {"console_log": "console.log", "network_log": "network.json"},
            "observations": {
                "console_messages": ["React hydration completed after 2400ms"],
                "network_idle_ms": 120,
                "dom_mutations_after_failure": 23,
            },
            "expected": {"required_fields": ["title"]},
            "actual": {"fields": {}, "array_length": 0},
            "labels": {"failure_type": "unknown", "confidence": 0.0},
            "safety": {
                "sanitized": True,
                "contains_credentials": False,
                "external_network_required": False,
                "user_authorized_or_synthetic": True,
            },
        }

        diagnosis = classify_failure_artifact(artifact)

        self.assertEqual(diagnosis["failure_type"], "async_hydration_timing")
        self.assertGreaterEqual(diagnosis["confidence"], 0.8)

    def test_classifier_detects_soft_rate_limit_and_obfuscation(self):
        soft_block = {
            "schema_version": "failure-artifact/v1",
            "run_id": "soft_block_001",
            "tool": "requests",
            "target_type": "sanitized_real_failure",
            "summary": "HTTP 200 with rate limit page",
            "error": {"message": "empty product list", "status_code": 200},
            "artifacts": {"html_snapshot": "snapshot.html"},
            "observations": {"body_text": "too many requests, slow down and try again later"},
            "expected": {"required_fields": ["items"]},
            "actual": {"fields": {}, "array_length": 0},
            "labels": {"failure_type": "unknown", "confidence": 0.0},
            "safety": {
                "sanitized": True,
                "contains_credentials": False,
                "external_network_required": False,
                "user_authorized_or_synthetic": True,
            },
        }
        obfuscated = {
            **soft_block,
            "run_id": "obfuscation_001",
            "tool": "node",
            "summary": "Bundle changed to eval wrapper",
            "error": {"message": "Cannot find exported parser after webpack chunk load", "status_code": None},
            "observations": {"bundle_markers": ["eval(", "_0x4f2a", "webpackJsonp"]},
        }

        self.assertEqual(classify_failure_artifact(soft_block)["failure_type"], "rate_limit_or_soft_block")
        self.assertEqual(classify_failure_artifact(obfuscated)["failure_type"], "js_bundle_obfuscation")

    def test_adapters_create_artifacts_from_playwright_scrapy_and_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_zip = root / "trace.zip"
            with ZipFile(trace_zip, "w") as archive:
                archive.writestr("trace.network", json.dumps({"status": 200, "url": "https://example.test/login"}))
                archive.writestr("trace.console", "React hydration completed after 1800ms")
                archive.writestr("trace.dom.html", "<html><input type='password'></html>")

            scrapy_log = root / "scrapy.log"
            scrapy_log.write_text("2026-06-25 DEBUG Crawled (403) <GET https://example.test/products>\n", encoding="utf-8")
            response = root / "response.html"
            response.write_text("<html>Forbidden</html>", encoding="utf-8")

            requests_json = root / "requests.json"
            requests_json.write_text(
                json.dumps({"status_code": 429, "url": "https://example.test/api", "body": "Too Many Requests"}),
                encoding="utf-8",
            )

            playwright = artifact_from_playwright_trace(trace_zip, run_id="pw_trace")
            scrapy = artifact_from_scrapy_run(scrapy_log, response, run_id="scrapy_run")
            requests_artifact = artifact_from_requests_run(requests_json, run_id="requests_run")

            self.assertEqual(playwright["tool"], "playwright")
            self.assertEqual(playwright["error"]["status_code"], 200)
            self.assertIn("html_snapshot", playwright["artifacts"])
            self.assertEqual(scrapy["tool"], "scrapy")
            self.assertEqual(scrapy["error"]["status_code"], 403)
            self.assertEqual(requests_artifact["tool"], "requests")
            self.assertEqual(requests_artifact["error"]["status_code"], 429)

    def test_playwright_trace_adapter_extracts_jsonl_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_zip = root / "trace.zip"
            with ZipFile(trace_zip, "w") as archive:
                archive.writestr(
                    "trace.trace",
                    "\n".join(
                        [
                            json.dumps(
                                {
                                    "type": "console",
                                    "message": {
                                        "type": "error",
                                        "text": "Timeout 30000ms waiting for selector .price",
                                    },
                                }
                            ),
                            json.dumps(
                                {
                                    "type": "event",
                                    "method": "Network.responseReceived",
                                    "params": {
                                        "response": {
                                            "url": "https://example.test/products",
                                            "status": 503,
                                            "request": {"method": "GET"},
                                        }
                                    },
                                }
                            ),
                        ]
                    ),
                )
                archive.writestr("resources/page.html", "<html><body>Service unavailable</body></html>")

            artifact = artifact_from_playwright_trace(trace_zip, run_id="pw_jsonl")

            self.assertEqual(artifact["run_id"], "pw_jsonl")
            self.assertEqual(artifact["error"]["status_code"], 503)
            self.assertEqual(artifact["observations"]["url"], "https://example.test/products")
            self.assertIn("Timeout 30000ms waiting for selector .price", artifact["error"]["message"])
            self.assertIn("Timeout 30000ms waiting for selector .price", artifact["observations"]["console_messages"])
            self.assertEqual(
                artifact["observations"]["network_events"],
                [{"method": "GET", "url": "https://example.test/products", "status": 503}],
            )
            self.assertIn("Service unavailable", artifact["observations"]["html_excerpt"])

    def test_playwright_trace_adapter_handles_malformed_mixed_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_zip = root / "trace.zip"
            with ZipFile(trace_zip, "w") as archive:
                archive.writestr("trace.trace", '{"type":"console","message":{"text":"first line ok"}}\n{bad json')
                archive.writestr("errors.log", "request failed with HTTP 429 after retry")
                archive.writestr("snapshot.dom", "<html><form><input type='password'></form></html>")

            artifact = artifact_from_playwright_trace(trace_zip, run_id="pw_malformed")

            self.assertEqual(artifact["run_id"], "pw_malformed")
            self.assertEqual(artifact["error"]["status_code"], 429)
            self.assertIn("first line ok", artifact["observations"]["console_messages"])
            self.assertIn("password", artifact["observations"]["html_excerpt"])
            self.assertEqual(artifact["observations"]["network_events"], [])

    def test_generate_synthetic_fixture_writes_replay_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "pack"
            out = root / "fixtures"
            pack.mkdir()
            artifact = {
                "schema_version": "failure-artifact/v1",
                "run_id": "selector_001",
                "tool": "playwright",
                "target_type": "sanitized_real_failure",
                "summary": "Selector changed",
                "error": {"message": "Timeout waiting for selector .price", "status_code": 200},
                "artifacts": {},
                "observations": {"missing_selectors": [".price"]},
                "expected": {"required_fields": ["price"]},
                "actual": {"fields": {}, "array_length": None},
                "labels": {"failure_type": "selector_drift", "confidence": 0.86},
                "safety": {
                    "sanitized": True,
                    "contains_credentials": False,
                    "external_network_required": False,
                    "user_authorized_or_synthetic": True,
                },
            }
            (pack / "failure_artifact.json").write_text(json.dumps(artifact), encoding="utf-8")

            result = generate_synthetic_fixture(pack, out)

            self.assertTrue(result["ok"])
            fixture_dir = Path(result["fixture_path"])
            self.assertTrue((fixture_dir / "failure_artifact.json").exists())
            self.assertIn("selector_drift", (fixture_dir / "replay_metadata.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
