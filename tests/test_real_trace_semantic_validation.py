import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.failure_artifacts.adapters import artifact_from_playwright_trace
from tools.failure_artifacts.classifier import classify_failure_artifact


FORBIDDEN_SYNTHETIC_FIELDS = (
    "storageStateExpected",
    "storage_state_expected",
    "routeRegistered",
    "route_registered",
    "shadowHost",
    "shadow_host",
    "elementExistsInShadowDom",
    "element_exists_in_shadow_dom",
)


def before(call_id, api_name, params=None, start_time=1.0):
    return {
        "type": "before",
        "callId": call_id,
        "apiName": api_name,
        "params": params or {},
        "startTime": start_time,
    }


def after(call_id, message=None, stack=None):
    record = {"type": "after", "callId": call_id}
    if message:
        record["error"] = {"message": message}
        if stack:
            record["error"]["stack"] = stack
    return record


def response(url, status, headers=None, request_url=None, from_service_worker=False, from_cache=False):
    payload = {
        "url": url,
        "status": status,
        "headers": headers or {},
        "request": {"url": request_url or url, "method": "GET"},
    }
    if from_service_worker:
        payload["fromServiceWorker"] = True
    if from_cache:
        payload["fromCache"] = True
    return {"type": "event", "method": "Network.responseReceived", "params": {"response": payload}}


def request(url, timestamp=2.0):
    return {
        "type": "event",
        "method": "Network.requestWillBeSent",
        "params": {"request": {"url": url, "method": "GET"}, "timestamp": timestamp},
    }


def console(text):
    return {
        "type": "event",
        "method": "Runtime.consoleAPICalled",
        "params": {"args": [{"value": text}]},
    }


def frame(url):
    return {"type": "event", "method": "Page.frameNavigated", "params": {"frame": {"url": url}}}


def exception(message):
    return {
        "type": "event",
        "method": "Runtime.exceptionThrown",
        "params": {"exceptionDetails": {"exception": {"description": message}}},
    }


class RealTraceSemanticValidationTests(unittest.TestCase):
    def _diagnose(self, records, *, html=""):
        with tempfile.TemporaryDirectory() as tmp:
            trace_zip = Path(tmp) / "trace.zip"
            raw_trace = "\n".join(json.dumps(record) for record in records)
            for forbidden in FORBIDDEN_SYNTHETIC_FIELDS:
                self.assertNotIn(forbidden, raw_trace)
            with ZipFile(trace_zip, "w") as archive:
                archive.writestr("trace.trace", raw_trace)
                if html:
                    archive.writestr("resources/page.html", html)
            artifact = artifact_from_playwright_trace(trace_zip)
            return artifact, classify_failure_artifact(artifact)

    def test_twenty_real_trace_semantic_fixtures_are_diagnosable_without_custom_fields(self):
        cases = [
            (
                "login redirect 302",
                [
                    before("c1", "page.goto", {"url": "https://app.example.test/dashboard"}),
                    response("https://app.example.test/dashboard", 302, {"location": "https://app.example.test/login"}),
                    frame("https://app.example.test/login"),
                    after("c1"),
                ],
                "",
                "playwright_storage_state_context",
                "login_redirect_after_authenticated_action",
            ),
            (
                "401 missing auth",
                [
                    before("c1", "page.goto", {"url": "https://app.example.test/account"}),
                    response("https://app.example.test/api/account", 401),
                    after("c1"),
                ],
                "",
                "playwright_storage_state_context",
                "login_redirect_after_authenticated_action",
            ),
            (
                "session expired console",
                [
                    before("c1", "page.click", {"selector": "text=Billing"}),
                    console("session expired; unauthorized, please log in"),
                    frame("https://app.example.test/login"),
                    after("c1", "Timeout 30000ms exceeded after redirect to login"),
                ],
                "",
                "playwright_storage_state_context",
                "login_redirect_after_authenticated_action",
            ),
            (
                "route registered too late",
                [
                    request("https://app.example.test/api/products", timestamp=999.0),
                    before("c2", "browserContext.route", {"url": "**/api/products"}, start_time=2.0),
                    after("c2"),
                ],
                "",
                "playwright_route_mock_har",
                "route_registered_too_late",
            ),
            (
                "route pattern mismatch",
                [
                    before("c1", "page.route", {"url": "**/api/products"}, start_time=1.0),
                    after("c1"),
                    request("https://app.example.test/api/v2/products", timestamp=2.0),
                ],
                "",
                "playwright_route_mock_har",
                "route_pattern_mismatch",
            ),
            (
                "HAR file missing",
                [
                    before("c1", "page.routeFromHAR", {"har": "fixtures/api.har", "notFound": "abort"}, start_time=1.0),
                    {"type": "event", "method": "Network.loadingFailed", "params": {"errorText": "net::ERR_FILE_NOT_FOUND"}},
                    after("c1"),
                ],
                "",
                "playwright_route_mock_har",
                "har_not_found_or_not_loaded",
            ),
            (
                "HAR fallback live network",
                [
                    before("c1", "browserContext.routeFromHAR", {"har": "fixtures/api.har", "notFound": "fallback"}, start_time=1.0),
                    after("c1"),
                    request("https://app.example.test/api/missing-in-har", timestamp=2.0),
                    response("https://app.example.test/api/missing-in-har", 200),
                ],
                "",
                "playwright_route_mock_har",
                "har_fallback_network_leak",
            ),
            (
                "shadow DOM boundary",
                [
                    before("c1", "locator.click", {"selector": "my-widget >> button.submit"}, start_time=1.0),
                    after("c1", "locator.click: Timeout 30000ms exceeded; resolved to 0 elements"),
                ],
                "<my-widget><template shadowrootmode='open'><button class='submit'>Save</button></template></my-widget>",
                "playwright_shadow_dom_locator",
                "shadow_root_boundary",
            ),
            (
                "custom element not upgraded",
                [
                    before("c1", "locator.click", {"selector": "checkout-button >> button"}, start_time=1.0),
                    console("customElements.get('checkout-button') is undefined; custom element not upgraded"),
                    after("c1", "locator.click: Timeout 30000ms exceeded waiting for custom element"),
                ],
                "<checkout-button></checkout-button>",
                "playwright_shadow_dom_locator",
                "custom_element_not_upgraded",
            ),
            (
                "host locator clicked instead of inner button",
                [
                    before("c1", "locator.click", {"selector": "checkout-button"}, start_time=1.0),
                    after("c1", "locator.click clicked custom element host; intended inner button was not targeted"),
                ],
                "<checkout-button><template shadowrootmode='open'><button>Pay</button></template></checkout-button>",
                "playwright_shadow_dom_locator",
                "locator_targets_host_not_inner_node",
            ),
            (
                "strict mode violation",
                [before("c1", "locator.click", {"selector": "button"}, 1.0), after("c1", "strict mode violation: locator('button') resolved to 2 elements")],
                "",
                "playwright_strict_mode_violation",
                "locator_multiple_matches",
            ),
            (
                "popup missed",
                [before("c1", "page.waitForEvent", {"event": "popup"}, 1.0), after("c1", "Timeout 30000ms exceeded while waiting for event \"popup\"")],
                "",
                "playwright_popup",
                "popup_page",
            ),
            (
                "download not saved",
                [before("c1", "page.waitForEvent", {"event": "download"}, 1.0), after("c1", "Timeout 30000ms exceeded waiting for download event; saveAs was not called")],
                "",
                "playwright_download",
                "download_event",
            ),
            (
                "service worker cache stale",
                [
                    request("https://app.example.test/api/products", 1.0),
                    response("https://app.example.test/api/products", 200, from_service_worker=True, from_cache=True),
                    console("stale cache response served from service worker"),
                ],
                "",
                "playwright_service_worker_cache",
                "stale_cache",
            ),
            (
                "execution context destroyed",
                [before("c1", "page.evaluate", {"expression": "window.appState"}, 1.0), after("c1", "Execution context was destroyed, most likely because of a navigation")],
                "",
                "playwright_execution_context_destroyed",
                "navigation_race",
            ),
            (
                "navigation timeout",
                [before("c1", "page.goto", {"url": "https://app.example.test/reports"}, 1.0), after("c1", "Timeout 30000ms exceeded while waiting until load")],
                "",
                "async_hydration_timing",
                None,
            ),
            (
                "proxy failed",
                [request("https://app.example.test", 1.0), exception("net::ERR_PROXY_CONNECTION_FAILED while loading page")],
                "",
                "network_http_error",
                "proxy_connection_failed",
            ),
            (
                "DNS failed",
                [request("https://missing.example.test", 1.0), exception("net::ERR_NAME_NOT_RESOLVED for missing.example.test")],
                "",
                "network_http_error",
                "dns_name_not_resolved",
            ),
            (
                "response shape changed",
                [
                    request("https://app.example.test/api/products", 1.0),
                    response("https://app.example.test/api/products", 200),
                    console("parser expected JSON key price; response now contains amount; schema validation failed"),
                ],
                "",
                "website_change",
                "response_shape_changed",
            ),
            (
                "selector drift",
                [before("c1", "locator.click", {"selector": ".old-submit"}, 1.0), after("c1", "Timeout 30000ms waiting for selector .old-submit; element not found")],
                "<button data-testid='submit'>Submit</button>",
                "selector_drift",
                None,
            ),
        ]

        self.assertEqual(len(cases), 20)
        for name, records, html, expected_type, expected_subtype in cases:
            with self.subTest(case=name):
                artifact, diagnosis = self._diagnose(records, html=html)
                self.assertEqual(diagnosis["failure_type"], expected_type, artifact["observations"])
                if expected_subtype:
                    self.assertEqual(diagnosis.get("subtype"), expected_subtype, diagnosis)

