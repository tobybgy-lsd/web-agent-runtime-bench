from __future__ import annotations

import argparse
import json
import shutil
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse


GENERATED_BY = "tools/real_trace_generation/generate_real_trace_fixtures.py"


@dataclass(frozen=True)
class Expected:
    failure_layer: str
    technical_category: str
    subtype: str | None
    evidence_level: str = "inferred"
    safe_next_action: bool = True


@dataclass(frozen=True)
class Case:
    case_id: str
    title: str
    source_urls: list[str]
    expected: Expected
    runner: str
    input_type: str = "native_playwright_trace_zip"
    description: str = ""


class LocalFailureSite(BaseHTTPRequestHandler):
    server_version = "AgentFailureDoctorFixture/0.8"

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            return self._html("<h1>Agent Failure Doctor local fixture</h1>")
        if path == "/selector":
            return self._html("<main><button data-testid='submit'>Submit</button></main>")
        if path == "/login-redirect":
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return
        if path == "/login":
            return self._html("<form><input name='user'><button>Sign in</button></form>")
        if path == "/auth-401" or path == "/api/auth-401":
            return self._json({"error": "unauthorized"}, status=401)
        if path == "/session-expired":
            return self._html("<script>console.error('session expired unauthorized please log in')</script><h1>Login</h1>")
        if path == "/route-page":
            return self._html("<script>fetch('/api/products').catch(() => {})</script><h1>Products</h1>")
        if path == "/api/products":
            return self._json({"items": [{"id": 1, "amount": 10}], "next": None})
        if path == "/api/v2/products":
            return self._json({"items": [{"id": 1, "amount": 10}]})
        if path == "/shadow":
            return self._html(
                """
                <my-widget></my-widget>
                <script>
                customElements.define('my-widget', class extends HTMLElement {
                  constructor() {
                    super();
                    const root = this.attachShadow({mode: 'open'});
                    root.innerHTML = '<button class="submit">Save</button>';
                  }
                });
                </script>
                """
            )
        if path == "/custom-not-upgraded":
            return self._html("<checkout-button></checkout-button><script>console.error('custom element not upgraded')</script>")
        if path == "/host-inner":
            return self._html(
                """
                <checkout-button></checkout-button>
                <script>
                customElements.define('checkout-button', class extends HTMLElement {
                  constructor() {
                    super();
                    const root = this.attachShadow({mode: 'open'});
                    root.innerHTML = '<button>Pay</button>';
                  }
                });
                console.error('custom element host clicked; intended inner button was not targeted');
                </script>
                """
            )
        if path == "/strict":
            return self._html("<button>Save</button><button>Save</button>")
        if path == "/popup":
            return self._html("<button id='open'>Open</button><script>document.querySelector('#open').onclick=()=>{}</script>")
        if path == "/download":
            return self._html("<button id='download'>Download</button>")
        if path == "/service-worker":
            return self._html(
                """
                <script>
                if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');
                console.error('stale cache response served from service worker');
                </script>
                <h1>Cached</h1>
                """
            )
        if path == "/sw.js":
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(b"self.addEventListener('fetch', event => {});")
            return
        if path == "/slow":
            return self._html("<script>setTimeout(()=>document.body.append('late'), 5000)</script>")
        if path == "/target-closed":
            return self._html("<button id='x'>Close</button>")
        if path == "/response-shape":
            return self._html("<script>fetch('/api/products').then(()=>console.error('parser expected JSON key price; response now contains amount; schema validation failed'))</script>")
        if path == "/endpoint-old":
            return self._json({"error": "not found", "new": "/api/v2/products"}, status=404)
        if path == "/graphql":
            return self._json({"errors": [{"message": "Cannot query field oldPrice on type Product"}]})
        if path == "/pagination":
            return self._json({"items": [], "message": "next cursor missing"})
        if path == "/login-flow":
            return self._html("<h1>New MFA consent page</h1><script>console.error('login flow changed new MFA consent page')</script>")
        if path == "/download-changed":
            return self._html("<script>console.error('download changed from direct link to async export job; download event never fires')</script>")
        if path == "/cdp":
            return self._html("<script>console.error('CDP websocket silent disconnect; cdp client not initialized')</script>")
        if path == "/loop":
            return self._html("<script>console.error('agent infinite loop repeatedly executed same action extract_content action')</script>")
        if path == "/docker":
            return self._html("<script>console.error('browser executable missing in docker headless environment')</script>")
        if path == "/next-step-download":
            return self._html("<script>console.error('download not available to next step; file was not saved')</script>")
        if path == "/rate-limit":
            return self._html("Too many requests. Slow down and try again later.", status=429)
        if path == "/challenge":
            return self._html("<h1>Verify you are human</h1><p>Local simulated challenge page</p>", status=403)
        if path == "/signature":
            return self._json({"error": "dynamic signature required; missing sign token"}, status=403)
        return self._html("<h1>Not Found</h1>", status=404)

    def _html(self, body: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"<!doctype html><html><body>{body}</body></html>".encode("utf-8"))

    def _json(self, payload: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate local native Playwright trace fixtures.")
    parser.add_argument("--out", default="examples/realistic_playwright_traces")
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args(argv)

    try:
        from playwright.sync_api import Error, TimeoutError, sync_playwright
    except Exception:
        print('Playwright is required for trace generation. Run: pip install -e ".[trace-gen]"')
        print("Then install the browser: python -m playwright install chromium")
        return 2

    out_root = Path(args.out)
    if args.clean and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer(("127.0.0.1", 0), LocalFailureSite)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    cases = build_cases()
    selected = cases[: args.count]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for case in selected:
                case_dir = out_root / case.case_id
                case_dir.mkdir(parents=True, exist_ok=True)
                trace_path = case_dir / "trace.zip"
                context = browser.new_context(accept_downloads=False)
                context.tracing.start(screenshots=True, snapshots=True, sources=True)
                page = context.new_page()
                try:
                    run_case(case.runner, page, context, base_url, TimeoutError, Error)
                except Exception as exc:
                    message = str(exc)
                    if "Page.goto" in message and "Timeout" in message:
                        pass
                    elif "Target page, context or browser has been closed" in message:
                        pass
                    else:
                        try:
                            page.evaluate("message => console.error(message)", message[:300])
                        except Exception:
                            pass
                finally:
                    context.tracing.stop(path=str(trace_path))
                    context.close()
                write_case_metadata(case_dir, case)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(f"generated {len(selected)} trace fixtures in {out_root}")
    return 0


def build_cases() -> list[Case]:
    docs = ["https://playwright.dev/docs/trace-viewer"]
    return [
        Case("01_selector_drift", "Selector drift", ["https://github.com/microsoft/playwright/issues/10611"], Expected("website_change", "selector_drift", None), "selector_drift"),
        Case("02_login_redirect_302", "Login redirect 302", ["https://github.com/microsoft/playwright/issues/20182"], Expected("automation_engineering", "playwright_storage_state_context", "login_redirect_after_authenticated_action"), "login_redirect"),
        Case("03_auth_401_missing_cookie", "401 missing auth", ["https://github.com/microsoft/playwright/issues/39380"], Expected("automation_engineering", "playwright_storage_state_context", "login_redirect_after_authenticated_action"), "auth_401"),
        Case("04_session_expired_console", "Session expired console", ["https://github.com/microsoft/playwright/issues/20182"], Expected("automation_engineering", "playwright_storage_state_context", "login_redirect_after_authenticated_action"), "session_expired"),
        Case("05_route_registered_too_late", "Route registered too late", ["https://github.com/microsoft/playwright/issues/21405"], Expected("automation_engineering", "playwright_route_mock_har", "route_registered_too_late"), "route_too_late"),
        Case("06_route_pattern_mismatch", "Route pattern mismatch", ["https://github.com/microsoft/playwright/issues/15553"], Expected("automation_engineering", "playwright_route_mock_har", "route_pattern_mismatch"), "route_pattern"),
        Case("07_har_file_missing_or_fallback", "HAR file missing", ["https://github.com/microsoft/playwright/issues/21405"], Expected("automation_engineering", "playwright_route_mock_har", "har_not_found_or_not_loaded"), "har_missing"),
        Case("08_live_network_leak_after_mock", "HAR fallback live network", ["https://github.com/microsoft/playwright/issues/21405"], Expected("automation_engineering", "playwright_route_mock_har", "har_fallback_network_leak"), "har_fallback"),
        Case("09_shadow_dom_boundary", "Shadow DOM boundary", ["https://github.com/microsoft/playwright/issues/23047"], Expected("automation_engineering", "playwright_shadow_dom_locator", "shadow_root_boundary"), "shadow_boundary"),
        Case("10_custom_element_not_upgraded", "Custom element not upgraded", ["https://github.com/microsoft/playwright/issues/33547"], Expected("automation_engineering", "playwright_shadow_dom_locator", "custom_element_not_upgraded"), "custom_not_upgraded"),
        Case("11_host_locator_instead_of_inner_button", "Host locator clicked instead of inner button", ["https://github.com/microsoft/playwright/issues/23047"], Expected("automation_engineering", "playwright_shadow_dom_locator", "locator_targets_host_not_inner_node"), "host_inner"),
        Case("12_strict_mode_violation", "Strict mode violation", ["https://github.com/microsoft/playwright/issues/10611"], Expected("automation_engineering", "playwright_strict_mode_violation", "locator_multiple_matches"), "strict"),
        Case("13_response_shape_changed", "Response shape changed", docs, Expected("website_change", "website_change", "response_shape_changed"), "response_shape"),
        Case("14_endpoint_changed_404_to_v2", "Endpoint changed", docs, Expected("website_change", "website_change", "api_endpoint_changed"), "endpoint_changed"),
        Case("15_graphql_schema_changed", "GraphQL schema changed", docs, Expected("website_change", "website_change", "graphql_schema_changed"), "graphql"),
        Case("16_pagination_cursor_missing", "Pagination cursor missing", docs, Expected("website_change", "website_change", "pagination_changed"), "pagination"),
        Case("17_login_flow_changed", "Login flow changed", docs, Expected("website_change", "website_change", "login_flow_changed"), "login_flow"),
        Case("18_download_behavior_changed", "Download behavior changed", docs, Expected("website_change", "website_change", "download_behavior_changed"), "download_changed"),
        Case("19_navigation_timeout", "Navigation timeout", ["https://github.com/microsoft/playwright/issues/12393"], Expected("automation_engineering", "async_hydration_timing", None), "navigation_timeout"),
        Case("20_execution_context_destroyed", "Execution context destroyed", docs, Expected("automation_engineering", "playwright_execution_context_destroyed", "navigation_race"), "execution_destroyed"),
        Case("21_target_closed", "Target closed", docs, Expected("environment", "playwright_browser_context_closed", "target_closed"), "target_closed"),
        Case("22_download_not_saved", "Download not saved", ["https://github.com/browser-use/browser-use/issues/1913"], Expected("automation_engineering", "playwright_download", "download_event"), "download_not_saved"),
        Case("23_service_worker_cache_stale", "Service worker cache stale", docs, Expected("automation_engineering", "playwright_service_worker_cache", "stale_cache"), "service_worker"),
        Case("24_cdp_websocket_disconnect_log_pack", "CDP websocket disconnect", ["https://github.com/browser-use/browser-use/issues/4579"], Expected("environment", "cdp_websocket_disconnected", "websocket_disconnect"), "cdp"),
        Case("25_agent_repeated_action_loop_log_pack", "Agent repeated action loop", ["https://github.com/browser-use/browser-use/issues/3779"], Expected("automation_engineering", "agent_repetition_loop", "repeated_action_loop"), "loop"),
        Case("26_docker_browser_executable_missing_log_pack", "Docker browser executable missing", ["https://github.com/browser-use/browser-use/issues/1331"], Expected("environment", "toolchain_environment", None), "docker"),
        Case("27_download_not_available_to_next_step_log_pack", "Download unavailable to next step", ["https://github.com/browser-use/browser-use/issues/1913"], Expected("automation_engineering", "playwright_download", "download_event"), "next_step_download"),
        Case("28_rate_limited_429_local", "Rate limited 429 local", docs, Expected("anti_bot_risk", "anti_bot_risk", "rate_limited"), "rate_limit"),
        Case("29_captcha_or_challenge_page_local", "Captcha/challenge local", docs, Expected("anti_bot_risk", "anti_bot_risk", "captcha_or_challenge_page"), "challenge"),
        Case("30_dynamic_signature_required_local", "Dynamic signature required local", docs, Expected("anti_bot_risk", "anti_bot_risk", "dynamic_signature_required"), "signature"),
    ]


def run_case(name: str, page, context, base_url: str, TimeoutError, Error) -> None:
    timeout = 700
    if name == "selector_drift":
        page.goto(f"{base_url}/selector")
        page.locator(".old-submit").click(timeout=timeout)
    elif name == "login_redirect":
        page.goto(f"{base_url}/login-redirect", wait_until="domcontentloaded", timeout=2000)
        page.wait_for_url("**/dashboard", timeout=timeout)
    elif name == "auth_401":
        page.goto(f"{base_url}/auth-401", wait_until="domcontentloaded", timeout=2000)
        page.evaluate("console.error('unauthorized 401 missing cookie please log in')")
    elif name == "session_expired":
        page.goto(f"{base_url}/session-expired", wait_until="domcontentloaded", timeout=2000)
        page.wait_for_url("**/dashboard", timeout=timeout)
    elif name == "route_too_late":
        page.goto(f"{base_url}/route-page", wait_until="domcontentloaded", timeout=2000)
        page.route("**/api/products", lambda route: route.fulfill(status=200, body="{}"))
    elif name == "route_pattern":
        page.route("**/api/products", lambda route: route.fulfill(status=200, body="{}"))
        page.goto(f"{base_url}/api/v2/products", wait_until="domcontentloaded", timeout=2000)
    elif name == "har_missing":
        page.route_from_har("missing-fixture.har", not_found="abort")
    elif name == "har_fallback":
        har = Path("tmp") / "empty-real-trace-fixture.har"
        har.parent.mkdir(exist_ok=True)
        har.write_text(json.dumps({"log": {"version": "1.2", "creator": {"name": "afd", "version": "0.8"}, "entries": []}}), encoding="utf-8")
        page.route_from_har(str(har), not_found="fallback")
        page.goto(f"{base_url}/api/products", wait_until="domcontentloaded", timeout=2000)
    elif name == "shadow_boundary":
        page.goto(f"{base_url}/shadow")
        page.locator("my-widget >> button.missing").click(timeout=timeout)
    elif name == "custom_not_upgraded":
        page.goto(f"{base_url}/custom-not-upgraded")
        page.locator("checkout-button >> button").click(timeout=timeout)
    elif name == "host_inner":
        page.goto(f"{base_url}/host-inner")
        page.locator("checkout-button").click(timeout=timeout)
        page.evaluate("console.error('custom element host clicked; intended inner button was not targeted')")
    elif name == "strict":
        page.goto(f"{base_url}/strict")
        page.locator("button").click(timeout=timeout)
    elif name == "response_shape":
        page.goto(f"{base_url}/response-shape", wait_until="domcontentloaded", timeout=2000)
        page.wait_for_timeout(200)
    elif name == "endpoint_changed":
        page.goto(f"{base_url}/endpoint-old", wait_until="domcontentloaded", timeout=2000)
        page.evaluate("console.error('old endpoint returned 404; links now point to /api/v2/products')")
    elif name == "graphql":
        page.goto(f"{base_url}/graphql", wait_until="domcontentloaded", timeout=2000)
        page.evaluate("console.error('Cannot query field oldPrice on type Product')")
    elif name == "pagination":
        page.goto(f"{base_url}/pagination", wait_until="domcontentloaded", timeout=2000)
        page.evaluate("console.error('pagination next cursor missing')")
    elif name == "login_flow":
        page.goto(f"{base_url}/login-flow", wait_until="domcontentloaded", timeout=2000)
    elif name == "download_changed":
        page.goto(f"{base_url}/download-changed", wait_until="domcontentloaded", timeout=2000)
    elif name == "navigation_timeout":
        page.goto(f"{base_url}/slow", wait_until="load", timeout=1)
    elif name == "execution_destroyed":
        page.goto(f"{base_url}/selector")
        page.evaluate("console.error('Execution context was destroyed, most likely because of a navigation')")
    elif name == "target_closed":
        page.goto(f"{base_url}/target-closed")
        page.evaluate("console.error('Target page, context or browser has been closed')")
        page.close()
        page.locator("#x").click(timeout=timeout)
    elif name == "download_not_saved":
        page.goto(f"{base_url}/download")
        page.wait_for_event("download", timeout=timeout)
    elif name == "service_worker":
        page.goto(f"{base_url}/service-worker", wait_until="domcontentloaded", timeout=2000)
        page.wait_for_timeout(300)
    elif name == "cdp":
        page.goto(f"{base_url}/cdp", wait_until="domcontentloaded", timeout=2000)
    elif name == "loop":
        page.goto(f"{base_url}/loop", wait_until="domcontentloaded", timeout=2000)
    elif name == "docker":
        page.goto(f"{base_url}/docker", wait_until="domcontentloaded", timeout=2000)
    elif name == "next_step_download":
        page.goto(f"{base_url}/next-step-download", wait_until="domcontentloaded", timeout=2000)
    elif name == "rate_limit":
        page.goto(f"{base_url}/rate-limit", wait_until="domcontentloaded", timeout=2000)
    elif name == "challenge":
        page.goto(f"{base_url}/challenge", wait_until="domcontentloaded", timeout=2000)
    elif name == "signature":
        page.goto(f"{base_url}/signature", wait_until="domcontentloaded", timeout=2000)
        page.evaluate("console.error('dynamic signature required missing sign token')")


def write_case_metadata(case_dir: Path, case: Case) -> None:
    expected = {
        "failure_layer": case.expected.failure_layer,
        "technical_category": case.expected.technical_category,
        "subtype": case.expected.subtype,
        "evidence_level": case.expected.evidence_level,
        "safe_next_action": case.expected.safe_next_action,
    }
    (case_dir / "expected_diagnosis.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    source = {
        "case_id": case.case_id,
        "source_type": "local_reproduction_from_public_pattern",
        "source_urls": case.source_urls,
        "generated_by": GENERATED_BY,
        "contains_custom_observation_fields": False,
        "contains_credentials": False,
        "contains_real_third_party_data": False,
        "sanitized_dummy_cookie": False,
    }
    (case_dir / "source.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
    (case_dir / "README.md").write_text(
        f"# {case.case_id}\n\n"
        f"{case.title}\n\n"
        f"- Input type: {case.input_type}\n"
        f"- Expected technical category: `{case.expected.technical_category}`\n"
        f"- Expected subtype: `{case.expected.subtype}`\n"
        f"- Safe next action: `{case.expected.safe_next_action}`\n"
        f"- Generated by: `{GENERATED_BY}`\n",
        encoding="utf-8",
    )
    pack = case_dir / "optional_input_pack"
    pack.mkdir(exist_ok=True)
    (pack / "user_description.txt").write_text(f"{case.title}\n", encoding="utf-8")
    (pack / "error.log").write_text(f"{case.title}\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
