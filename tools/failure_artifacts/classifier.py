"""Rule-based failure classifier for web automation artifacts.

No LLM calls. No network. Pure local rule matching against structured evidence.
"""

from __future__ import annotations

import json
from typing import Any, Mapping


def _combined_text(artifact: Mapping[str, Any]) -> str:
    return json.dumps(artifact, ensure_ascii=False).lower()


def _error_focused_text(artifact: Mapping[str, Any], *, include_user_description: bool = False) -> str:
    """Return a narrower text blob focused on direct failure signals."""
    parts: list[str] = []
    error = artifact.get("error")
    if isinstance(error, Mapping):
        parts.append(str(error.get("message") or ""))
        parts.append(str(error.get("stack") or ""))
    observations = artifact.get("observations")
    if isinstance(observations, Mapping):
        parts.append(str(observations.get("log_excerpt") or ""))
        if include_user_description:
            parts.append(str(observations.get("user_description") or ""))
        network_events = observations.get("network_events")
        if isinstance(network_events, list):
            for event in network_events[:10]:
                if isinstance(event, Mapping):
                    parts.append(json.dumps(event, ensure_ascii=False))
        console_messages = observations.get("console_messages")
        if isinstance(console_messages, list):
            parts.extend(str(message) for message in console_messages[:10])
        exception_details = observations.get("exception_details")
        if isinstance(exception_details, list):
            for detail in exception_details[:5]:
                if isinstance(detail, Mapping):
                    parts.append(str(detail.get("message") or ""))
                    parts.append(str(detail.get("stack") or ""))
        parts.append(str(observations.get("body_text") or ""))
        parts.append(str(observations.get("html_excerpt") or ""))
        snapshot_excerpts = observations.get("snapshot_excerpts")
        if isinstance(snapshot_excerpts, list):
            for excerpt in snapshot_excerpts[:5]:
                if isinstance(excerpt, Mapping):
                    parts.append(str(excerpt.get("excerpt") or ""))
    return " ".join(parts).lower()


def _result(
    failure_type: str,
    confidence: float,
    evidence: list[str],
    suggested_fix: list[str],
    can_auto_fix: bool = False,
    subtype: str | None = None,
    evidence_level: str | None = None,
) -> dict[str, Any]:
    result = {
        "failure_type": failure_type,
        "confidence": round(confidence, 2),
        "evidence": evidence,
        "suggested_fix": suggested_fix,
        "can_auto_fix": can_auto_fix,
        "synthetic_only": True,
    }
    if subtype:
        result["subtype"] = subtype
    if evidence_level:
        result["evidence_level"] = evidence_level
    return result


def _classify_cross_framework_adapter_hint(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    if not isinstance(observations, Mapping):
        return None
    hint = observations.get("adapter_failure_hint")
    if not isinstance(hint, Mapping):
        return None
    technical = str(hint.get("technical_category") or "").strip()
    subtype = str(hint.get("subtype") or "").strip()
    if not technical:
        return None
    framework = str(hint.get("framework") or "unknown")
    layer = str(hint.get("failure_layer") or "automation_engineering")
    error_family = str(hint.get("error_family") or subtype or technical)
    evidence = [
        f"cross-framework adapter hint: framework={framework}",
        f"detected error family: {error_family}",
    ]
    result = _result(
        technical,
        0.94 if technical != "insufficient_evidence" else 0.35,
        evidence,
        _cross_framework_adapter_fix_suggestions(technical, subtype, framework),
        subtype=subtype or None,
        evidence_level="adapter_normalized",
    )
    result["failure_layer"] = layer
    return result


def _cross_framework_adapter_fix_suggestions(technical: str, subtype: str, framework: str) -> list[str]:
    generic = [
        f"treat this as a {framework} failure normalized into Agent Failure Doctor evidence",
        "run `failure-doctor plan` on the report before editing code",
        "keep sanitized logs and framework_metadata.json with the regression case",
    ]
    specific: dict[str, str] = {
        "selector_drift": "update the stale selector or wait condition from current DOM evidence",
        "popup_or_overlay_blocking": "handle the blocking overlay or popup before clicking the target",
        "navigation_or_wait_timeout": "replace fixed waits with a semantic ready/navigation condition",
        "browser_driver_mismatch": "align browser, driver, and runtime versions before changing selectors",
        "selector_syntax_error": "fix the invalid CSS/XPath selector syntax",
        "popup_or_new_page": "switch to the correct window, tab, popup, or page before continuing",
        "target_closed_or_page_crash": "capture browser/runtime logs and prevent using a closed page target",
        "cdp_protocol_error": "separate CDP/runtime instability from page-level locator failures",
        "playwright_route_mock_har": "verify intercept/mock/HAR registration before the first matching request",
        "fixture_or_mock_missing": "restore the fixture/mock file and add a regression check for it",
        "environment_config_mismatch": "fix base URL and environment config before editing test logic",
        "browser_context_or_origin_policy": "handle the browser origin/context boundary explicitly",
        "viewport_responsive_layout_mismatch": "reproduce with the same viewport and update responsive selectors",
        "network_http_error": "verify proxy, DNS, TLS, and timeout settings before changing extraction code",
        "website_change": "update selectors, endpoints, or response parsing from fresh site evidence",
        "anti_bot_risk": "keep this as compliance triage; do not add access-control defeat logic",
        "insufficient_evidence": "collect error.log, console.txt, network.json, trace, or a minimal reproduction",
    }
    return [specific.get(technical, "review the normalized framework failure evidence before editing")] + generic


def _classify_runtime_api_missing(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    runtime_rules = (
        ("window", "missing_window", "globalThis.window"),
        ("document", "missing_document", "globalThis.document"),
        ("navigator", "missing_navigator", "globalThis.navigator"),
        ("eventtarget", "missing_event_target", "globalThis.EventTarget"),
        ("localstorage", "missing_local_storage", "globalThis.localStorage"),
    )
    for api, subtype, shim in runtime_rules:
        if api in text and ("is not defined" in text or "referenceerror" in text or "getitem" in text):
            return _result(
                "runtime_api_missing",
                0.9,
                [f"browser runtime API marker found: {api}", "failure happened before extraction completed"],
                [
                    f"provide a synthetic shim for {shim}",
                    "or run the bundle inside a browser context such as Playwright page.evaluate",
                    "add a regression case for this runtime surface",
                ],
                can_auto_fix=True,
                subtype=subtype,
            )
    return None


def _classify_captcha_or_bot_wall(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    focused = _error_focused_text(artifact, include_user_description=False)
    markers = ("captcha", "verify you are human", "are you human", "turnstile", "recaptcha", "cloudflare challenge", "just a moment")
    found = [marker for marker in markers if marker in focused]
    if not found:
        return None
    return _result(
        "captcha_or_bot_wall",
        0.88 if len(found) > 1 else 0.72,
        [f"challenge marker found: {marker}" for marker in found[:4]],
        [
            "stop automation and request authorized/manual review",
            "record as blocked, not as selector drift",
            "do not add challenge-solving or access-control circumvention logic",
        ],
    )


def _classify_js_bundle_obfuscation(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("eval(", "_0x", "webpackjsonp", "cannot find exported parser", "bundle changed", "obfuscated", "dynamic function")
    found = [marker for marker in markers if marker in text]
    if len(found) < 2:
        return None
    return _result(
        "js_bundle_obfuscation",
        0.82,
        [f"bundle/obfuscation marker found: {marker}" for marker in found[:4]],
        [
            "treat this as a bundle contract change, not a selector issue",
            "capture a new sanitized bundle fixture if sharing is allowed",
            "prefer stable public/user-authorized APIs over parsing obfuscated internals",
        ],
    )


def _classify_website_change(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    if _has_local_environment_error(artifact):
        return None

    observations = artifact.get("observations", {})
    if not isinstance(observations, Mapping):
        observations = {}

    evidence: list[str] = []
    subtype = ""

    if (
        observations.get("response_shape_changed") is True
        or "json key" in text
        or "schema validation failed" in text
        or "parser expected" in text
        or "response contains" in text
        or "response now contains" in text
        or "field renamed" in text
        or "key renamed" in text
        or "array renamed" in text
        or "field moved" in text
        or "json path" in text
        or "totalcount missing" in text
        or "price selector empty" in text
    ):
        subtype = "response_shape_changed"
        evidence.append("response JSON/schema shape changed")
        missing = observations.get("missing_json_keys")
        if isinstance(missing, list) and missing:
            evidence.append(f"missing JSON keys: {', '.join(map(str, missing[:5]))}")

    if not subtype and (
        observations.get("old_selector_missing") is True
        or ("old selector" in text and ("not found" in text or "missing" in text))
        or (
            ("selector" in text or "locator" in text)
            and (
                "not found" in text
                or "timed out" in text
                or "timeout waiting" in text
                or "missing" in text
                or "resolved to 0" in text
                or "0 elements" in text
            )
            and (
                "site redesign" in text
                or "layout release" in text
                or "viewport" in text
                or "now has" in text
                or "now contains" in text
                or "custom element" in text
                or "input[name=" in text
            )
        )
    ):
        subtype = "selector_drift"
        evidence.append("old selector is missing after a site change")
        if observations.get("similar_dom_candidate"):
            evidence.append(f"similar DOM candidate: {observations.get('similar_dom_candidate')}")

    if not subtype and (observations.get("dom_structure_changed") is True or "dom structure changed" in text):
        subtype = "dom_structure_changed"
        evidence.append("DOM structure changed compared with the previous script assumptions")
        if observations.get("old_dom_path") and observations.get("new_dom_path"):
            evidence.append(f"DOM path changed: {observations.get('old_dom_path')} -> {observations.get('new_dom_path')}")

    if not subtype and (
        observations.get("api_endpoint_changed") is True
        or "endpoint changed" in text
        or "network shows" in text
        or "links now point to" in text
        or "returned 301 to" in text
        or ("old endpoint" in text and "new endpoint" in text)
    ):
        subtype = "api_endpoint_changed"
        evidence.append("network endpoint appears to have changed")
        if observations.get("old_endpoint") or observations.get("new_endpoint"):
            evidence.append(f"endpoint: {observations.get('old_endpoint')} -> {observations.get('new_endpoint')}")

    if not subtype and ("cannot query field" in text or observations.get("graphql_error")):
        subtype = "graphql_schema_changed"
        evidence.append("GraphQL schema rejected a previously valid field")
        if observations.get("graphql_error"):
            evidence.append(f"GraphQL error: {observations.get('graphql_error')}")

    if not subtype and (
        observations.get("pagination_changed") is True
        or "next cursor missing" in text
        or "next page button replaced" in text
        or "button.next not found" in text
        or "cursor token" in text
        or "pagination" in text and "cursor" in text
    ):
        subtype = "pagination_changed"
        evidence.append("pagination contract changed or the next cursor is missing")
        if observations.get("missing_cursor"):
            evidence.append(f"missing cursor: {observations.get('missing_cursor')}")

    if not subtype and (
        observations.get("login_flow_changed") is True
        or "login flow changed" in text
        or "new mfa" in text
        or "consent page" in text
        or "terms confirmation" in text
        or "callback contains auth_code" in text
    ):
        subtype = "login_flow_changed"
        evidence.append("login flow gained a new step or page")
        if observations.get("new_step"):
            evidence.append(f"new login step: {observations.get('new_step')}")

    if not subtype and (
        observations.get("download_behavior_changed") is True
        or "download changed" in text
        or "download event absent" in text
        or "download event never fires" in text
        or "export job" in text
        or "exportjobid" in text
        or "fileurl later" in text
        or "notification api returns" in text
        or ("direct link" in text and "async" in text)
    ):
        subtype = "download_behavior_changed"
        evidence.append("download behavior changed from the previous automation contract")
        if observations.get("old_download_mode") or observations.get("new_download_mode"):
            evidence.append(
                f"download mode: {observations.get('old_download_mode')} -> {observations.get('new_download_mode')}"
            )

    if not subtype:
        return None

    return _result(
        "website_change",
        0.9,
        evidence,
        _website_change_fix_suggestions(subtype),
        subtype=subtype,
        evidence_level="confirmed" if observations else "inferred",
    )


def _website_change_fix_suggestions(subtype: str) -> list[str]:
    specific = {
        "selector_drift": "re-record or inspect the new DOM and replace the stale selector with a stable role/test id/structural locator",
        "dom_structure_changed": "update selector scopes to match the new DOM hierarchy and add a snapshot regression",
        "api_endpoint_changed": "update the endpoint URL, method, or route pattern from the latest network evidence",
        "response_shape_changed": "update JSON paths/schema mapping and add guards for missing or renamed fields",
        "graphql_schema_changed": "update the GraphQL query to match the current schema and add a schema regression fixture",
        "pagination_changed": "update cursor/next-page extraction and stop conditions from the latest response",
        "login_flow_changed": "update the authorized login preflight for the new MFA/consent step without collecting secrets",
        "download_behavior_changed": "update the script for the new export/download flow and wait for the final file event",
    }
    return [
        specific.get(subtype, "update the automation contract from new DOM/network evidence"),
        "capture a fresh sanitized trace, DOM snapshot, and network.json before editing the script",
        "ask Codex to update selectors, endpoints, JSON paths, or flow steps from the new evidence",
        "add a regression test that locks the new site contract",
    ]


def _has_local_environment_error(artifact: Mapping[str, Any]) -> bool:
    focused = _error_focused_text(artifact, include_user_description=False)
    local_markers = (
        "filenotfounderror",
        "no such file or directory",
        "enoent",
        "permission denied",
        "modulenotfounderror",
        "browser executable missing",
        "executable doesn't exist",
    )
    return any(marker in focused for marker in local_markers)


def _classify_header_normalization_evidence_gap(
    artifact: Mapping[str, Any], text: str
) -> dict[str, Any] | None:
    focused = _error_focused_text(artifact, include_user_description=False)
    markers = (
        "wsgi normalized",
        "werkzeug",
        "title-case",
        "raw http/2",
        "raw transport",
        "header evidence lost",
        "application boundary",
    )
    if not any(marker in focused for marker in markers):
        return None
    return _result(
        "insufficient_evidence",
        0.94,
        [
            "application/framework logs may have normalized request header names",
            "raw transport/header evidence is missing or inconclusive",
        ],
        [
            "capture raw transport evidence, proxy-level logs, or a packet-level reproduction before changing request code",
            "record the framework boundary that normalized headers so later diagnosis does not confuse logging artifacts with protocol behavior",
            "rerun diagnosis with sanitized raw request/response metadata if available",
        ],
        subtype="header_normalization_evidence_gap",
        evidence_level="evidence_gap",
    )


def _classify_anti_bot_risk(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    if not isinstance(observations, Mapping):
        observations = {}
    status = artifact.get("error", {}).get("status_code") or observations.get("status_code")
    focused = _error_focused_text(artifact, include_user_description=False)

    evidence: list[str] = []
    subtype = ""

    if (
        "automation descriptor" in focused
        or "webdriver descriptor" in focused
        or ("navigator.webdriver" in focused and "descriptor" in focused)
        or ("navigator prototype" in focused and "webdriver" in focused)
    ):
        subtype = "automation_descriptor_detected"
        evidence.append("automation descriptor evidence found at the browser/runtime boundary")

    if not subtype and (
        "wasm signature" in focused
        or "webassembly" in focused and "signature" in focused
        or "wasm" in focused and "verification failed" in focused
    ):
        subtype = "wasm_signature_verification_failed"
        evidence.append("WebAssembly/request-integrity signature verification failed")

    if not subtype and (
        "obfuscated js integrity required" in focused
        or ("protected script" in focused and "request acceptance" in focused)
        or ("front-end script integrity boundary" in focused and "403" in focused)
    ):
        subtype = "obfuscated_js_integrity_required"
        evidence.append("obfuscated JavaScript request-integrity boundary evidence found")

    if not subtype and (
        "js ast obfuscation detected" in focused
        or ("ast obfuscation" in focused and "bundle summary" in focused)
        or ("control-flow flattening" in focused and "computed property access" in focused)
        or ("obfuscated request-integrity logic" in focused and "bundle summary" in focused)
    ):
        subtype = "js_ast_obfuscation_detected"
        evidence.append("sanitized JavaScript bundle summary shows AST-level obfuscation evidence")

    if not subtype and (
        "rotated string array detected" in focused
        or ("string-array rotation" in focused and "request integrity" in focused)
        or ("string-array indirection" in focused and "bundle summary" in focused)
    ):
        subtype = "rotated_string_array_detected"
        evidence.append("sanitized JavaScript bundle summary shows rotated string-array evidence")

    if not subtype and (
        "client generated token missing" in focused
        or ("script-produced integrity evidence is absent" in focused)
        or ("browser script did not produce integrity parameter" in focused)
    ):
        subtype = "client_generated_token_missing"
        evidence.append("request is missing client-generated integrity evidence")

    if not subtype and (
        "request integrity algorithm changed" in focused
        or ("request integrity algorithm drift" in focused)
        or ("previously valid client token" in focused and "rejected" in focused)
    ):
        subtype = "request_integrity_algorithm_changed"
        evidence.append("authorized regression indicates request-integrity algorithm drift")

    if not subtype and (
        "client-side signature required" in focused
        or "client side signature required" in focused
        or "x-client-sign" in focused
        or ("request integrity token" in focused and ("missing" in focused or "absent" in focused))
        or "ast deobfuscation" in focused
        or "decryption failed" in focused
        or "key decryption" in focused
    ):
        subtype = "client_side_signature_required"
        evidence.append("client-side request-integrity signature appears required")

    if not subtype and (
        "distributed token bucket" in focused
        or "distributed rate limit" in focused
        or ("shared quota" in focused and "worker" in focused)
        or ("concurrent workers" in focused and "retry-after" in focused)
    ):
        subtype = "distributed_rate_limit_detected"
        evidence.append("distributed/shared-quota rate-limit evidence found")
        if status:
            evidence.append(f"HTTP status code observed: {status}")

    if not subtype and (
        "rate limit scheduler" in focused
        or "scheduler needed" in focused
        or ("circuit breaker" in focused and "pacing" in focused)
        or ("backoff" in focused and "queue-level pacing" in focused)
    ):
        subtype = "rate_limit_scheduler_needed"
        evidence.append("rate-limit evidence indicates scheduler/backoff handling is needed")
        if status:
            evidence.append(f"HTTP status code observed: {status}")

    if not subtype and (
        "decoy response or data poisoning" in focused
        or ("decoy response" in focused and "data poisoning" in focused)
        or ("canary rows" in focused and "poisoned" in focused)
    ):
        subtype = "decoy_response_or_data_poisoning"
        evidence.append("HTTP response may be syntactically valid but untrustworthy due to decoy/poisoning evidence")

    if not subtype and (
        "session device binding" in focused
        or "device binding risk" in focused
        or "session/device/ip binding" in focused
        or ("same account" in focused and "device id" in focused and "binding" in focused)
    ):
        subtype = "session_device_binding_risk"
        evidence.append("session/device/network binding risk marker found")
        if status:
            evidence.append(f"HTTP status code observed: {status}")

    if not subtype and (
        "header protocol mismatch" in focused
        or ("http/2" in focused and "pseudo-header" in focused and "app-level logs" in focused)
        or ("client hints" in focused and "transport metadata" in focused)
        or ("h2 header casing" in focused and "captured transport" in focused)
    ):
        subtype = "header_protocol_mismatch"
        evidence.append("raw transport/header evidence conflicts with app-level framework logs")

    if not subtype and (
        "client hints platform mismatch" in focused
        or ("sec-ch-ua-platform" in focused and "navigator.platform" in focused and "inconsistent" in focused)
        or ("user-agent" in focused and "sec-ch-ua-platform" in focused and "platform evidence differ" in focused)
    ):
        subtype = "client_hints_platform_mismatch"
        evidence.append("browser runtime and Client Hints platform evidence are inconsistent")

    if not subtype and (
        "browser header consistency risk" in focused
        or ("ua" in focused and "sec-ch-ua" in focused and "runtime metadata conflict" in focused)
        or ("browser headers" in focused and "runtime metadata" in focused and "conflict" in focused)
    ):
        subtype = "browser_header_consistency_risk"
        evidence.append("browser header, Client Hints, and runtime metadata consistency risk found")

    if not subtype and (
        "canvas fingerprint collision" in focused
        or "duplicate canvas fingerprint" in focused
        or ("duplicate canvas hash" in focused and "session" in focused)
        or ("headless cluster" in focused and "canvas fingerprint" in focused)
    ):
        subtype = "canvas_fingerprint_collision"
        evidence.append("duplicate Canvas fingerprint evidence repeats across sessions")

    if not subtype and (
        "browser canvas fingerprint risk" in focused
        or ("canvas hash uniqueness audit" in focused and "failed" in focused)
        or ("canvas fingerprint" in focused and "authorized test telemetry" in focused)
    ):
        subtype = "browser_canvas_fingerprint_risk"
        evidence.append("browser Canvas fingerprint consistency risk evidence found")

    if not subtype and (
        "webgl virtual renderer detected" in focused
        or ("webgl" in focused and "virtual renderer" in focused)
        or ("webgl renderer" in focused and ("swiftshader" in focused or "mesa" in focused or "virtualized" in focused))
    ):
        subtype = "webgl_virtual_renderer_detected"
        evidence.append("sanitized WebGL renderer/vendor evidence suggests a virtualized browser runtime")

    if not subtype and (
        "webrtc private ip leak detected" in focused
        or ("webrtc" in focused and "private ip" in focused)
        or ("ice candidate" in focused and "private network" in focused)
        or ("ice candidate" in focused and "private-range" in focused)
    ):
        subtype = "webrtc_private_ip_leak_detected"
        evidence.append("sanitized WebRTC/ICE evidence indicates a private network topology leak")

    if not subtype and (
        "automation global scope leak detected" in focused
        or ("global scope" in focused and "automation globals" in focused)
        or ("global namespace" in focused and "automation" in focused)
    ):
        subtype = "automation_global_scope_leak_detected"
        evidence.append("sanitized browser global-scope evidence contains automation namespace leakage")

    if not subtype and (
        "js vmp integrity check failed" in focused
        or "client vm signature mismatch" in focused
        or ("client vm" in focused and "integrity" in focused and "mismatch" in focused)
    ):
        subtype = "js_vmp_integrity_check_failed"
        evidence.append("sanitized client-VM integrity evidence failed verification")

    if not subtype and (
        "numeric semantics mismatch" in focused
        or ("javascript numeric coercion" in focused and "differs" in focused)
        or ("runtime arithmetic" in focused and "differs" in focused)
    ):
        subtype = "numeric_semantics_mismatch"
        evidence.append("sanitized runtime arithmetic evidence differs across client/server semantics")

    if not subtype and (
        "http/2 settings fingerprint mismatch" in focused
        or "http2 settings fingerprint mismatch" in focused
        or ("http/2 settings" in focused and "browser protocol stack" in focused)
        or ("http2 settings" in focused and "settings-family-differs" in focused)
    ):
        subtype = "http2_settings_fingerprint_mismatch"
        evidence.append("sanitized HTTP/2 SETTINGS evidence differs from browser protocol-stack evidence")

    if not subtype and (
        "ja4 h2 fingerprint mismatch" in focused
        or ("ja4" in focused and "h2" in focused and "mismatch" in focused)
        or ("protocol stack mismatch" in focused and "ja4" in focused)
    ):
        subtype = "ja4_h2_fingerprint_mismatch"
        evidence.append("sanitized JA4/H2 evidence differs from the expected browser protocol stack")

    if not subtype and (
        "zero interval input detected" in focused
        or ("average key interval" in focused and "0" in focused and "variance 0" in focused)
        or ("impossible key intervals" in focused and "input timing" in focused)
    ):
        subtype = "zero_interval_input_detected"
        evidence.append("sanitized input timing evidence reports impossible zero-interval input")

    if not subtype and (
        "keystroke telemetry anomaly" in focused
        or ("input timing summary" in focused and "impossible key interval distribution" in focused)
        or ("input telemetry anomaly" in focused and "bulk fill" in focused)
    ):
        subtype = "keystroke_telemetry_anomaly"
        evidence.append("sanitized keystroke/input telemetry evidence is anomalous")

    if not subtype and (
        "behavioral input risk" in focused
        or ("fixed interval input timing" in focused and "authorized test telemetry" in focused)
        or ("fixed interval input timing" in focused and "input timing summary" in focused)
    ):
        subtype = "behavioral_input_risk"
        evidence.append("sanitized input timing evidence suggests a behavioral input consistency risk")

    if not subtype and (
        "pointer trajectory entropy anomaly" in focused
        or ("movement summary" in focused and "low vertical deviation" in focused)
        or ("vertical deviation" in focused and "too-low" in focused)
    ):
        subtype = "pointer_trajectory_entropy_anomaly"
        evidence.append("sanitized pointer trajectory evidence reports low movement entropy")

    if not subtype and (
        "mathematical trajectory detected" in focused
        or ("pointer acceleration" in focused and "too deterministic" in focused)
        or ("acceleration profile" in focused and "too-deterministic" in focused)
    ):
        subtype = "mathematical_trajectory_detected"
        evidence.append("sanitized pointer trajectory evidence appears overly deterministic")

    if not subtype and (
        "tls alpn fingerprint mismatch" in focused
        or ("alpn" in focused and "http/1.1" in focused and "h2" in focused)
        or ("standard http client" in focused and "browser path" in focused and "h2" in focused)
    ):
        subtype = "tls_alpn_fingerprint_mismatch"
        evidence.append("standard HTTP client and browser TLS/ALPN evidence differ")

    if not subtype and (
        "transport fingerprint risk" in focused
        or ("tls handshake" in focused and "alpn" in focused and "http version" in focused)
        or ("tls/alpn/http version" in focused and "evidence" in focused)
    ):
        subtype = "transport_fingerprint_risk"
        evidence.append("transport-layer fingerprint evidence differs from browser/runtime evidence")

    if not subtype and (
        "debugger timing anomaly" in focused
        or ("debugger timing" in focused and "threshold" in focused)
        or ("runtime timing" in focused and "execution threshold" in focused)
    ):
        subtype = "debugger_timing_anomaly"
        evidence.append("sanitized runtime timing evidence indicates a debugger/timing anomaly")

    if not subtype and (
        "native function integrity mismatch" in focused
        or ("function.prototype" in focused and "reflection" in focused)
        or ("native reflection" in focused and "mismatch" in focused)
    ):
        subtype = "native_function_integrity_mismatch"
        evidence.append("sanitized native-function reflection evidence differs from browser runtime expectations")

    if not subtype and (
        "runtime sandbox leak detected" in focused
        or ("sandbox leak" in focused and "browser runtime" in focused)
        or ("node/process globals" in focused and "browser runtime" in focused)
        or ("server-runtime-global" in focused and "browser runtime" in focused)
    ):
        subtype = "runtime_sandbox_leak_detected"
        evidence.append("sanitized runtime evidence indicates a browser sandbox/global leakage boundary")

    if not subtype and (status == 429 or "too many requests" in focused or "rate limit" in focused):
        subtype = "rate_limited"
        evidence.append("rate-limit marker found")
        if status:
            evidence.append(f"HTTP status code observed: {status}")

    if not subtype and (
        "decoy data" in focused
        or "poisoned" in focused
        or "trusted canary" in focused
        or "schema looks valid" in focused
        or "fake prices" in focused
        or "valid looking product list" in focused
    ):
        subtype = "data_poisoning_decoy_response"
        evidence.append("HTTP 200 response contains decoy/poisoning evidence instead of trustworthy data")

    if not subtype and (
        "every 100 requests" in focused
        or ("401" in focused and "periodic" in focused)
        or "token lifecycle" in focused
        or "stateful anomaly" in focused
        or "session refreshes" in focused
        or "refresh token recovers" in focused
    ):
        subtype = "stateful_session_lifecycle_anomaly"
        evidence.append("periodic auth/session failures suggest a stateful lifecycle anomaly")

    if not subtype and (
        observations.get("behavioral_risk") is True
        or "behavioral" in focused
        or "trajectory" in focused
        or "mouse" in focused
        or "slide" in focused
        or "unusual traffic" in focused
        or ("request burst" in focused and "triggered" in focused)
        or "high-frequency" in focused
        or "after burst" in focused
        or "same query returns empty data" in focused
        or "temporarily blocked" in focused
        or "slow down" in focused
        or "security verification" in focused
        or "repeated attempts" in focused
        or "temporary hold" in focused
        or "deviation detected" in focused
        or "mathematical trajectory" in focused
        or "entropy audit failed" in focused
    ):
        subtype = "behavioral_risk"
        evidence.append("behavioral risk marker found in request pattern or page text")

    if not subtype and (
        observations.get("headless_headed_mismatch") is True
        or ("headless" in focused and "headed" in focused and ("blocked" in focused or "succeeds" in focused))
        or "fingerprint" in focused
        or "ja3" in focused
        or "ja4" in focused
        or "http/2" in focused
        or "client hints" in focused
        or "webrtc" in focused
        or "webgl" in focused
        or "prototype hook" in focused
        or "tostring output" in focused
        or "sandbox leak" in focused
        or "virtualized audio" in focused
        or "audio fingerprint" in focused
        or "audio hardware detected" in focused
        or "p0f" in focused
        or "tcp/ip" in focused
        or "os mismatch" in focused
    ):
        subtype = "fingerprint_risk"
        evidence.append("environment protocol or fingerprint mismatch detected")

    signature_markers = ("signature", "x-bogus", "x-s", "x-sign", "dynamic token")
    found_signature = [marker for marker in signature_markers if marker in focused]
    if not subtype and found_signature:
        subtype = "dynamic_signature_required"
        evidence.extend(f"dynamic request signature marker found: {marker}" for marker in found_signature[:3])

    challenge_markers = ("captcha", "challenge page", "verify you are human", "cf-ray", "cloudflare", "akamai", "datadome", "perimeterx", "kasada")
    found_challenge = [marker for marker in challenge_markers if marker in focused]
    if not subtype and found_challenge:
        subtype = "captcha_or_challenge_page"
        evidence.extend(f"challenge marker found: {marker}" for marker in found_challenge[:4])

    if not subtype and (
        observations.get("ip_reputation_block") is True
        or "ip reputation" in focused
        or ("current network" in focused and "approved" in focused)
    ):
        subtype = "ip_reputation_block"
        evidence.append("access differs by network or source reputation")

    if not subtype and (
        observations.get("ip_reputation_block") is True
        or "risk control page" in focused
        or "risk page" in focused
        or "x-risk-action" in focused
        or "x-risk" in focused
        or "waiting room page" in focused
    ):
        subtype = "ip_reputation_block"
        evidence.append("platform risk or waiting-room page suggests source/access reputation review")

    if not subtype and (
        status == 403
        or "lacks permission" in focused
        or "permission block" in focused
        or "access denied" in focused
        or "access warning" in focused
        or "action requires manual review" in focused
        or "manual review" in focused
        or "action denied" in focused
        or "role lacks" in focused
        or "policy warning" in focused
        or "automated export not allowed" in focused
    ):
        subtype = "auth_or_permission_block"
        evidence.append("authorization or permission block marker found")
        if status:
            evidence.append(f"HTTP status code observed: {status}")

    if not subtype:
        return None

    confidence = (
        0.94
        if subtype
        in {
            "data_poisoning_decoy_response",
            "decoy_response_or_data_poisoning",
            "stateful_session_lifecycle_anomaly",
            "automation_descriptor_detected",
            "wasm_signature_verification_failed",
            "client_side_signature_required",
            "distributed_rate_limit_detected",
            "rate_limit_scheduler_needed",
            "session_device_binding_risk",
            "header_protocol_mismatch",
            "tls_alpn_fingerprint_mismatch",
            "transport_fingerprint_risk",
            "client_hints_platform_mismatch",
            "browser_header_consistency_risk",
            "canvas_fingerprint_collision",
            "browser_canvas_fingerprint_risk",
            "webgl_virtual_renderer_detected",
            "webrtc_private_ip_leak_detected",
            "automation_global_scope_leak_detected",
            "js_vmp_integrity_check_failed",
            "numeric_semantics_mismatch",
            "http2_settings_fingerprint_mismatch",
            "ja4_h2_fingerprint_mismatch",
            "keystroke_telemetry_anomaly",
            "zero_interval_input_detected",
            "behavioral_input_risk",
            "pointer_trajectory_entropy_anomaly",
            "mathematical_trajectory_detected",
            "debugger_timing_anomaly",
            "native_function_integrity_mismatch",
            "runtime_sandbox_leak_detected",
            "obfuscated_js_integrity_required",
            "js_ast_obfuscation_detected",
            "rotated_string_array_detected",
            "client_generated_token_missing",
            "request_integrity_algorithm_changed",
        }
        else 0.93
        if subtype == "dynamic_signature_required"
        else (
            0.92
            if subtype
            in {
                "rate_limited",
                "captcha_or_challenge_page",
                "ip_reputation_block",
                "auth_or_permission_block",
                "fingerprint_risk",
                "behavioral_risk",
            }
            else 0.88
        )
    )
    return _result(
        "anti_bot_risk",
        confidence,
        evidence,
        _anti_bot_risk_safe_suggestions(subtype),
        subtype=subtype,
        evidence_level="confirmed",
    )


def _anti_bot_risk_safe_suggestions(subtype: str) -> list[str]:
    if subtype in {
        "obfuscated_js_integrity_required",
        "js_ast_obfuscation_detected",
        "rotated_string_array_detected",
        "client_generated_token_missing",
        "request_integrity_algorithm_changed",
    }:
        return [
            "treat this as a protected JavaScript/request-integrity boundary, not a selector/storage/proxy bug",
            "collect sanitized JS bundle metadata, function-name summaries, request-parameter diffs, and HTTP rejection evidence before changing automation code",
            "use an official API, authorized SDK, documented export, or platform-approved test hook when available",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {"dynamic_signature_required", "client_side_signature_required", "wasm_signature_verification_failed"}:
        return [
            "treat this as a protected request-integrity boundary, not a selector/storage/proxy bug",
            "use an official API, authorized SDK, documented export, or platform-approved integration when available",
            "verify local clock skew, nonce freshness, parameter ordering, canonical serialization, and URL encoding against authorized documentation",
            "capture sanitized request metadata and stop the run if authorization or platform terms are unclear",
        ]
    if subtype == "automation_descriptor_detected":
        return [
            "treat browser automation descriptor evidence as an access-policy signal, not a parser or selector bug",
            "confirm the automation is authorized and use documented test or partner integrations where available",
            "capture sanitized browser/runtime metadata for diagnosis without adding evasion logic",
            "stop the run if authorization or platform terms are unclear",
        ]
    if subtype in {"data_poisoning_decoy_response", "decoy_response_or_data_poisoning"}:
        return [
            "treat HTTP 200 decoy data as a trust-boundary signal, not a successful scrape",
            "compare trusted evidence, canary records, and authorized export/API output before changing parsers",
            "add data-integrity assertions so plausible but poisoned rows do not silently pass",
            "stop the run if authorization or data-access terms are unclear",
        ]
    if subtype in {"distributed_rate_limit_detected", "rate_limit_scheduler_needed"}:
        return [
            "treat distributed rate-limit evidence as a capacity and authorization boundary, not a transient selector bug",
            "add conservative pacing, retry-after handling, circuit breakers, and queue-level backoff in authorized environments",
            "prefer official bulk export, API quota negotiation, or platform-approved scheduling when available",
            "stop the run if authorization or data-access terms are unclear",
        ]
    if subtype == "session_device_binding_risk":
        return [
            "treat session/device binding evidence as an authorization and account-state boundary",
            "verify the run uses an authorized account, stable approved environment, and documented session lifecycle",
            "add fail-closed checkpoints for repeated auth degradation instead of increasing retries",
            "stop the run if authorization or data-access terms are unclear",
        ]
    if subtype == "header_protocol_mismatch":
        return [
            "treat header/protocol mismatch as an evidence-quality issue before changing request behavior",
            "capture sanitized raw transport evidence and compare it with framework-normalized logs",
            "verify HTTP version, client hints, and header normalization in an authorized reproduction",
            "stop the run if authorization or platform terms are unclear",
        ]
    if subtype in {"tls_alpn_fingerprint_mismatch", "transport_fingerprint_risk"}:
        return [
            "standard HTTP client and browser transport fingerprints are inconsistent; do not misclassify this as selector, storage, or proxy failure",
            "confirm whether an authorized API, official SDK, compliant export, or platform-approved integration exists",
            "collect sanitized TLS, ALPN, HTTP version, and transport metadata evidence before changing automation code",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {"client_hints_platform_mismatch", "browser_header_consistency_risk"}:
        return [
            "browser headers, Client Hints, and runtime metadata are inconsistent; do not misclassify this as selector, storage, or proxy failure",
            "confirm whether an authorized API, official SDK, compliant export, documented test hook, or platform-approved integration exists",
            "collect sanitized user-agent, Client Hints, navigator/runtime metadata, and HTTP-version evidence before changing automation code",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {"canvas_fingerprint_collision", "browser_canvas_fingerprint_risk"}:
        return [
            "browser Canvas fingerprint evidence is inconsistent or repeated across sessions; do not misclassify this as selector, storage, or proxy failure",
            "confirm whether an authorized API, official SDK, compliant export, documented test hook, or platform-approved integration exists",
            "collect sanitized Canvas hash/session-count evidence, browser/runtime metadata, and HTTP rejection evidence before changing automation code",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {
        "webgl_virtual_renderer_detected",
        "webrtc_private_ip_leak_detected",
        "automation_global_scope_leak_detected",
        "debugger_timing_anomaly",
        "native_function_integrity_mismatch",
        "runtime_sandbox_leak_detected",
    }:
        return [
            "browser runtime evidence indicates a fingerprint or sandbox boundary; do not misclassify this as selector, storage, or proxy failure",
            "confirm whether an authorized API, official SDK, compliant export, documented test hook, or platform-approved integration exists",
            "collect sanitized WebGL/WebRTC/runtime metadata, timing summaries, and HTTP rejection evidence before changing automation code",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {"http2_settings_fingerprint_mismatch", "ja4_h2_fingerprint_mismatch"}:
        return [
            "browser protocol-stack evidence is inconsistent with the standard client path; do not misclassify this as selector, storage, or proxy failure",
            "confirm whether an authorized API, official SDK, compliant export, or platform-approved integration exists",
            "collect sanitized ALPN, HTTP version, HTTP/2 SETTINGS, and protocol-stack evidence before changing automation code",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {"js_vmp_integrity_check_failed", "numeric_semantics_mismatch"}:
        return [
            "treat this as a protected client-VM/request-integrity boundary, not a selector/storage/proxy bug",
            "collect sanitized client-VM summaries, numeric-semantics evidence, request metadata, and HTTP rejection evidence",
            "use an official API, authorized SDK, documented export, or platform-approved test hook when available",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype in {
        "keystroke_telemetry_anomaly",
        "zero_interval_input_detected",
        "behavioral_input_risk",
        "pointer_trajectory_entropy_anomaly",
        "mathematical_trajectory_detected",
    }:
        return [
            "input timing telemetry is anomalous; do not misclassify this as selector, storage, or proxy failure",
            "confirm the run is an authorized test or approved automation workflow before continuing",
            "collect a sanitized input-timing summary and prefer official APIs, SDKs, test hooks, or compliant export paths when available",
            "stop automation when authorization or platform terms are unclear",
        ]
    if subtype == "stateful_session_lifecycle_anomaly":
        return [
            "build a request timeline that marks 401s, refresh events, session ids, and page indexes",
            "verify token/session lifecycle handling in an authorized test environment before increasing volume",
            "add checkpoints and resume logic that fail closed when repeated auth degradation appears",
            "stop the run if authorization or data-access terms are unclear",
        ]
    return [
        f"treat this as possible access-control or anti-abuse risk ({subtype}), not a selector/storage/proxy bug",
        "confirm authorization and data-access permission before continuing automation",
        "prefer official API, authorized export, manual review, or contacting the platform owner",
        "reduce request volume and stop the run if authorization or platform terms are unclear",
    ]


def _classify_auth_expiry(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    if artifact.get("tool") == "playwright":
        observations = artifact.get("observations", {})
        if isinstance(observations, Mapping):
            console_messages = " ".join(map(str, observations.get("console_messages", []))).lower()
            if any(marker in console_messages for marker in ("session expired", "unauthorized", "please log in")):
                return None
    markers = ("password", "login", "signin", "sign in", "session expired", "redirected_to_login")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    evidence = [f"auth/login marker found: {marker}" for marker in found[:3]]
    if artifact.get("error", {}).get("status_code") == 200:
        evidence.append("HTTP 200 returned but content indicates login/auth state")
    return _result(
        "auth_expiry",
        0.84,
        evidence,
        [
            "refresh authenticated session before scraping",
            "add a preflight login-state check",
            "re-run with valid storage_state or equivalent authorized session",
        ],
    )


def _classify_playwright_storage_state_context(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    if not isinstance(observations, Mapping):
        observations = {}
    if artifact.get("tool") != "playwright" and "playwright" not in text:
        return None

    auth_markers = ("login", "redirected_to_login", "401", "302", "missing_cookie", "storage_state", "storagestate")
    if not any(marker in text for marker in auth_markers):
        return None

    evidence: list[str] = []
    subtype = ""
    confidence = 0.83
    evidence_level = "confirmed"

    storage_state_expected = observations.get("storage_state_expected")
    storage_state_loaded = observations.get("storage_state_loaded")
    if storage_state_expected is True and storage_state_loaded is False:
        subtype = "storage_state_not_loaded"
        confidence = 0.92
        evidence.append("storageState was expected but not observed as loaded")

    if not subtype and observations.get("context_recreated") is True and not observations.get("new_context_storage_state"):
        subtype = "context_recreated_without_state"
        confidence = 0.88
        evidence.append("browser context was recreated without storageState after authenticated setup")

    missing_local_storage = observations.get("missing_local_storage_keys")
    if not subtype and isinstance(missing_local_storage, list) and missing_local_storage:
        subtype = "local_storage_missing"
        confidence = 0.87
        evidence.append(f"missing localStorage keys: {', '.join(map(str, missing_local_storage[:5]))}")

    base_url = observations.get("base_url")
    storage_origin = observations.get("storage_state_origin")
    if not subtype and base_url and storage_origin and _origin_host(str(base_url)) != _origin_host(str(storage_origin)):
        subtype = "base_url_state_origin_mismatch"
        confidence = 0.87
        evidence.append(f"baseURL host does not match storageState origin: {base_url} vs {storage_origin}")

    cookie_domain = observations.get("cookie_domain")
    current_host = observations.get("current_host")
    if not subtype and cookie_domain and current_host and not _cookie_domain_matches_host(str(cookie_domain), str(current_host)):
        subtype = "cookie_domain_mismatch"
        confidence = 0.87
        evidence.append(f"cookie domain does not match current host: {cookie_domain} vs {current_host}")

    if not subtype and observations.get("auth_redirect_detected") is True:
        subtype = "login_redirect_after_authenticated_action"
        confidence = 0.91 if observations.get("auth_status_code") == 401 else 0.86
        evidence_level = str(observations.get("storage_context_evidence_level") or "inferred")
        evidence.append("authenticated flow ended in a login/auth redirect in the trace")
        auth_status = observations.get("auth_status_code")
        if auth_status:
            evidence.append(f"auth-related HTTP status observed: {auth_status}")

    if not subtype:
        return None

    missing_cookies = observations.get("missing_cookie_names")
    if isinstance(missing_cookies, list) and missing_cookies:
        evidence.append(f"authenticated request missed cookies: {', '.join(map(str, missing_cookies[:5]))}")
    final_url = observations.get("final_url")
    if final_url:
        evidence.append(f"final URL indicates auth redirect or login page: {final_url}")
    response_chain = observations.get("response_chain")
    if isinstance(response_chain, list) and response_chain:
        statuses = []
        for item in response_chain[:5]:
            if isinstance(item, Mapping):
                status = item.get("status")
                url = item.get("url")
                statuses.append(f"{status} {url}" if url else str(status))
        if statuses:
            evidence.append(f"response chain: {' -> '.join(statuses)}")

    return _result(
        "playwright_storage_state_context",
        confidence,
        evidence,
        _storage_state_fix_suggestions(subtype),
        subtype=subtype,
        evidence_level=evidence_level,
    )


def _storage_state_fix_suggestions(subtype: str) -> list[str]:
    common = [
        "confirm storageState is created from the same authorized origin used by the failing test",
        "add a login-state preflight before the first authenticated request",
        """Playwright repair sketch:
```ts
const context = await browser.newContext({ storageState: 'playwright/.auth/user.json' });
const page = await context.newPage();
await page.goto(baseURL);
await expect(page).not.toHaveURL(/\\/login/);
```""",
    ]
    specific = {
        "cookie_domain_mismatch": "regenerate storageState on the target host, and check cookie domain/path/sameSite before reuse",
        "storage_state_not_loaded": "pass the storageState option to browser.newContext or test.use before creating the page",
        "context_recreated_without_state": "reuse the authenticated context or pass storageState each time a new context is created",
        "local_storage_missing": "verify localStorage/sessionStorage origins are present in the saved storageState JSON",
        "base_url_state_origin_mismatch": "align baseURL with the origin used to generate storageState, or maintain one state file per origin",
        "login_redirect_after_authenticated_action": "treat the trace as an auth-state failure candidate: verify storageState freshness, origin, and context creation before debugging selectors",
        "likely_storage_state_not_loaded": "confirm storageState is passed to browser.newContext or test.use before the failing action",
        "likely_auth_state_expired": "regenerate the authorized storageState and add a preflight assertion that the page is not redirected to login",
        "likely_context_lost_auth": "check whether a new browser context or page was created after login without carrying the authenticated state",
    }
    return [specific.get(subtype, "review storageState and browser context setup")] + common


def _origin_host(url: str) -> str:
    lowered = url.lower()
    without_scheme = lowered.split("://", 1)[-1]
    return without_scheme.split("/", 1)[0].split(":", 1)[0]


def _cookie_domain_matches_host(domain: str, host: str) -> bool:
    normalized_domain = domain.lower().lstrip(".")
    normalized_host = host.lower()
    return normalized_host == normalized_domain or normalized_host.endswith(f".{normalized_domain}")


def _classify_playwright_route_mock_har(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    if not isinstance(observations, Mapping):
        observations = {}
    if artifact.get("tool") != "playwright" and "playwright" not in text:
        return None

    markers = ("route", "mock", "har", "routefromhar", "live_network_request", "route_matched")
    if not any(marker in text for marker in markers):
        return None

    evidence: list[str] = []
    subtype = ""
    confidence = 0.84
    evidence_level = "inferred"

    if observations.get("route_registered_after_request") is True:
        subtype = "route_registered_too_late"
        confidence = 0.89
        evidence_level = "inferred" if observations.get("route_timing_basis") == "trace_order" else "confirmed"
        first_request = observations.get("first_request_url")
        if observations.get("route_timing_basis") == "trace_order":
            evidence.append("route registration appeared after the first network request in trace order")
        else:
            evidence.append("route was registered after the first matching request had already started")
        if first_request:
            evidence.append(f"first request was not intercepted: {first_request}")

    if not subtype and observations.get("har_expected") is True and observations.get("har_loaded") is False:
        subtype = "har_not_found_or_not_loaded"
        confidence = 0.88
        evidence_level = "confirmed"
        har_path = observations.get("har_path")
        evidence.append("HAR replay was expected but the HAR was not loaded")
        if har_path:
            evidence.append(f"HAR path: {har_path}")

    if not subtype and observations.get("har_loaded") is True and observations.get("har_not_found_policy") == "fallback" and observations.get("live_network_request") is True:
        subtype = "har_fallback_network_leak"
        confidence = 0.9
        evidence_level = "confirmed"
        evidence.append("routeFromHAR used fallback and allowed a live network request")
        if observations.get("har_miss_url"):
            evidence.append(f"HAR miss URL: {observations.get('har_miss_url')}")

    if not subtype and observations.get("mock_response_shape_mismatch") is True:
        subtype = "mock_response_shape_mismatch"
        confidence = 0.87
        evidence_level = "confirmed"
        expected = observations.get("expected_response_fields")
        actual = observations.get("actual_response_fields")
        evidence.append("mock response was fulfilled but response shape did not match expected fields")
        if isinstance(expected, list):
            evidence.append(f"expected response fields: {', '.join(map(str, expected[:5]))}")
        if isinstance(actual, list):
            evidence.append(f"actual response fields: {', '.join(map(str, actual[:5]))}")

    if not subtype and observations.get("route_registered") is True and observations.get("route_matched") is False:
        subtype = "route_pattern_mismatch"
        confidence = 0.87
        evidence_level = "confirmed"
        pattern = observations.get("route_pattern")
        request_url = observations.get("request_url")
        evidence.append("route pattern did not match request URL")
        if pattern:
            evidence.append(f"registered route pattern: {pattern}")
        if request_url:
            evidence.append(f"request URL: {request_url}")

    if not subtype:
        return None

    if observations.get("live_network_request") is True:
        evidence.append("request leaked to live network instead of being served by mock/HAR")
    if observations.get("har_error"):
        evidence.append(f"HAR error: {observations.get('har_error')}")

    return _result(
        "playwright_route_mock_har",
        confidence,
        evidence,
        _route_mock_har_fix_suggestions(subtype),
        subtype=subtype,
        evidence_level=evidence_level,
    )


def _route_mock_har_fix_suggestions(subtype: str) -> list[str]:
    common = [
        "register route or routeFromHAR before page.goto and before the request can start",
        "fail closed during debugging so unexpected requests do not silently hit live network",
        """Playwright route repair sketch:
```ts
await page.route('**/api/products/**', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: [] }),
  });
});
```""",
        """Playwright HAR repair sketch:
```ts
await page.routeFromHAR('fixtures/api.har', {
  url: '**/api/**',
  notFound: 'abort',
});
```""",
    ]
    specific = {
        "route_pattern_mismatch": "align the route glob/regex with the actual request URL and query shape",
        "route_registered_too_late": "move page.route or routeFromHAR setup before navigation and before agent actions",
        "har_not_found_or_not_loaded": "verify the HAR path exists relative to the test working directory and is loaded before navigation",
        "har_fallback_network_leak": "replace HAR fallback with abort while debugging, then update the HAR fixture for missing requests",
        "mock_response_shape_mismatch": "update the mocked JSON contract to match the parser/test expectations",
    }
    return [specific.get(subtype, "review route/mock/HAR setup")] + common


def _classify_playwright_shadow_dom_locator(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    if not isinstance(observations, Mapping):
        observations = {}
    if artifact.get("tool") != "playwright" and "playwright" not in text:
        return None

    markers = ("shadow", "custom_element", "custom element", "shadowroot", "shadow_root", "testid_inside_shadow")
    if not any(marker in text for marker in markers):
        return None

    evidence: list[str] = []
    subtype = ""
    confidence = 0.84
    evidence_level = "inferred"

    shadow_mode = observations.get("shadow_root_mode")
    if shadow_mode == "closed":
        subtype = "closed_shadow_root_unreachable"
        confidence = 0.93
        evidence_level = "confirmed"
        evidence.append("closed shadow root cannot be directly queried by Playwright locator")

    if not subtype and observations.get("custom_element_upgraded") is False:
        subtype = "custom_element_not_upgraded"
        confidence = 0.93
        evidence_level = "confirmed"
        evidence.append("custom element was not upgraded before locator action")

    if not subtype and observations.get("inner_node_not_targeted") is True:
        subtype = "locator_targets_host_not_inner_node"
        confidence = 0.93
        evidence_level = "confirmed"
        evidence.append("locator targeted the custom-element host instead of the intended inner node")

    if not subtype and observations.get("testid_inside_shadow_dom") is True and observations.get("missing_shadow_strategy") is True:
        subtype = "testid_inside_shadow_dom_missing_strategy"
        confidence = 0.93
        evidence_level = "confirmed"
        evidence.append("test id exists inside shadow DOM but no shadow-aware locator strategy was used")

    if not subtype and observations.get("element_exists_in_shadow_dom") is True and observations.get("ordinary_locator_failed") is True:
        subtype = "shadow_root_boundary"
        evidence_level = str(observations.get("shadow_evidence_level") or ("inferred" if observations.get("shadow_inferred_from_html") else "confirmed"))
        confidence = 0.88 if evidence_level == "inferred" else 0.93
        evidence.append("element exists inside shadow DOM, but the ordinary locator path was unreachable")

    if not subtype:
        return None

    host = observations.get("shadow_host")
    inner = observations.get("inner_selector") or observations.get("intended_inner_selector")
    if host:
        evidence.append(f"shadow host: {host}")
    if inner:
        evidence.append(f"intended inner selector: {inner}")
    testid = observations.get("testid")
    if testid:
        evidence.append(f"test id marker: {testid}")

    return _result(
        "playwright_shadow_dom_locator",
        confidence,
        evidence,
        _shadow_dom_fix_suggestions(subtype, observations),
        subtype=subtype,
        evidence_level=evidence_level,
    )


def _shadow_dom_fix_suggestions(subtype: str, observations: Mapping[str, Any]) -> list[str]:
    if subtype == "closed_shadow_root_unreachable":
        return [
            "Closed shadow root cannot be directly queried by Playwright locator.",
            "Expose a test hook, use public UI behavior, or ask the component owner to add test ids/accessibility roles.",
        ]

    host = str(observations.get("shadow_host") or observations.get("locator_target") or "my-component")
    inner = str(observations.get("inner_selector") or observations.get("intended_inner_selector") or "button")
    testid = str(observations.get("testid") or "submit-button")
    specific = {
        "shadow_root_boundary": "use a locator path that starts at the shadow host and then targets the inner control",
        "custom_element_not_upgraded": "wait for the custom element to be defined/upgraded before locating inside it",
        "locator_targets_host_not_inner_node": "target the actionable inner control instead of clicking the custom-element host",
        "testid_inside_shadow_dom_missing_strategy": "prefer a stable test id or accessible role exposed by the component contract",
    }
    return [
        specific.get(subtype, "review shadow DOM locator strategy"),
        """Playwright shadow DOM locator sketch:
```ts
await page.locator('""" + host + """').locator('""" + inner + """').click();
```""",
        """Test id strategy sketch:
```ts
await page.getByTestId('""" + testid + """').click();
```""",
        "add a regression fixture that records the host element and the intended inner control separately",
    ]


def _classify_rate_limit_or_soft_block(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    status = artifact.get("error", {}).get("status_code") or artifact.get("observations", {}).get("status_code")
    markers = (
        "too many requests",
        "slow down",
        "rate limit",
        "temporarily blocked",
        "try again later",
        "access denied",
        "unusual traffic",
        "empty product list",
    )
    found = [marker for marker in markers if marker in text]
    if status == 429 or len(found) >= 2:
        evidence = [f"soft block/rate-limit marker found: {marker}" for marker in found[:3]]
        if status:
            evidence.insert(0, f"HTTP status code observed: {status}")
        return _result(
            "rate_limit_or_soft_block",
            0.88 if status == 429 else 0.85,
            evidence,
            [
                "classify this as access/rate limiting before changing selectors",
                "reduce concurrency or add authorized backoff where appropriate",
                "do not add challenge-solving or access-control circumvention logic",
            ],
            subtype=f"http_{status}" if status else "soft_block_page",
        )
    return None


def _classify_network_http_error(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    focused = _error_focused_text(artifact)
    status = artifact.get("error", {}).get("status_code") or artifact.get("observations", {}).get("status_code")
    if status in (401, 403) or (isinstance(status, int) and status >= 500):
        subtype = f"http_{status}"
        evidence = [f"HTTP status code indicates transport/server failure: {status}"]
        return _result(
            "network_http_error",
            0.9 if status in (401, 403, 429) else 0.82,
            evidence,
            [
                "separate transport failure from extraction logic",
                "retry only when authorized and safe",
                "add backoff or session refresh where appropriate",
            ],
            subtype=subtype,
        )
    subtype_hints = artifact.get("observations", {}).get("subtype_hint") if isinstance(artifact.get("observations"), Mapping) else None
    if subtype_hints in {"proxy_connection_failed", "dns_name_not_resolved", "tls_certificate_error"}:
        return _result(
            "network_http_error",
            0.88,
            [f"transport subtype hint found: {subtype_hints}"],
            ["verify network/proxy/DNS/TLS settings before changing selectors", "capture response metadata separately from parser errors"],
            subtype=str(subtype_hints),
        )
    transport_markers = (
        "timeout waiting for response",
        '"network_error": "timeout"',
        "proxy",
        "err_name_not_resolved",
        "dns",
        "err_cert",
        "certificate",
        "tls",
        "connection reset",
        "empty response",
    )
    found = [marker for marker in transport_markers if marker in focused]
    if not found:
        return None
    subtype = "transport_error"
    if found[0] == "proxy":
        subtype = "proxy_connection_failed"
    elif found[0] in {"err_name_not_resolved", "dns"}:
        subtype = "dns_name_not_resolved"
    elif found[0] in {"err_cert", "certificate", "tls"}:
        subtype = "tls_certificate_error"
    return _result(
        "network_http_error",
        0.86,
        [f"transport marker found: {found[0]}"],
        ["retry with backoff if authorized", "capture response metadata separately from parser errors"],
        subtype=subtype,
    )


def _classify_async_hydration_timing(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    mutation_count = observations.get("dom_mutations_after_failure") if isinstance(observations, Mapping) else None
    network_idle_ms = observations.get("network_idle_ms") if isinstance(observations, Mapping) else None
    markers = (
        "hydration",
        "resolved to 0 elements before hydration",
        "network idle",
        "dom mutation",
        "after failure",
        "element appeared after timeout",
        "wait_until",
        "page.goto",
        "waiting until load",
        "timeout 30000ms exceeded",
        "timeout 1ms exceeded",
        "timeout exceeded",
    )
    found = [marker for marker in markers if marker in text]
    timing_evidence = []
    if isinstance(mutation_count, int) and mutation_count > 0:
        timing_evidence.append(f"DOM mutated after failure: {mutation_count} changes")
    if isinstance(network_idle_ms, int) and network_idle_ms < 500:
        timing_evidence.append(f"network idle window was short: {network_idle_ms}ms")
    if not found and not timing_evidence:
        return None
    return _result(
        "async_hydration_timing",
        0.84 if timing_evidence else 0.74,
        [f"timing marker found: {marker}" for marker in found[:3]] + timing_evidence,
        [
            "wait for a semantic ready condition instead of a fixed timeout",
            "capture DOM after hydration before extracting fields",
            "add a regression with delayed DOM mutation timing",
        ],
    )


def _classify_playwright_strict_mode_violation(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("strict mode violation", "resolved to 2 elements", "resolved to multiple elements")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_strict_mode_violation",
        0.87,
        [f"strict-mode marker found: {marker}" for marker in found[:3]],
        [
            "narrow the locator so it resolves to one intended element",
            "prefer role/text filters or scoped locators over broad CSS",
            "add a regression DOM snapshot with duplicate matches",
        ],
        subtype="locator_multiple_matches",
    )


def _classify_playwright_frame_locator(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("framelocator", "frame locator", "iframe", "waiting for frame", "frame was detached", "no frame found")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_frame_locator",
        0.84,
        [f"frame/iframe marker found: {marker}" for marker in found[:3]],
        [
            "wait for the iframe to attach before locating inside it",
            "scope selectors through frameLocator or the correct frame",
            "capture parent and frame DOM snapshots separately",
        ],
        subtype="iframe_locator",
    )


def _classify_playwright_browser_context_closed(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    if "popup" in text or "new page" in text or "waitforevent('popup'" in text:
        return None
    markers = (
        "target page, context or browser has been closed",
        "targetclosederror",
        "browser has been closed",
        "page has been closed",
        "context has been closed",
    )
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_browser_context_closed",
        0.88,
        [f"closed browser/page/context marker found: {found[0]}"],
        [
            "separate page lifecycle failure from locator failure",
            "check whether the page/context closes before the awaited action completes",
            "persist trace/screenshot/log before closing the browser context",
        ],
        subtype="target_closed",
    )


def _classify_playwright_execution_context_destroyed(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("execution context was destroyed", "most likely because of a navigation", "cannot find context with specified id")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_execution_context_destroyed",
        0.86,
        [f"navigation-race marker found: {marker}" for marker in found[:2]],
        [
            "wait for navigation/load state before evaluating page JavaScript",
            "avoid reusing element handles across navigation",
            "wrap the click and navigation wait in the same awaited block",
        ],
        subtype="navigation_race",
    )


def _classify_cdp_websocket_disconnected(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("cdp websocket", "websocket silent disconnect", "httpx.readerror", "browser session is alive", "cdp client not initialized")
    found = [marker for marker in markers if marker in text]
    if len(found) < 2 and "cdp client not initialized" not in text:
        return None
    return _result(
        "cdp_websocket_disconnected",
        0.87,
        [f"CDP/session transport marker found: {marker}" for marker in found[:3]],
        [
            "treat this as browser transport/session instability before changing page selectors",
            "capture browser process logs and CDP connection lifecycle",
            "add reconnect or fail-fast handling around remote browser sessions",
        ],
        subtype="websocket_disconnect",
    )


def _classify_agent_repetition_loop(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("infinite loop", "repeatedly executed", "same action", "extract_content action", "unknown led to infinite loop")
    found = [marker for marker in markers if marker in text]
    if len(found) < 2:
        return None
    return _result(
        "agent_repetition_loop",
        0.84,
        [f"agent repetition marker found: {marker}" for marker in found[:3]],
        [
            "add a repeated-action guard with a clear failure reason",
            "save the last few actions, observations, screenshots, and tool results",
            "return a structured diagnosis instead of continuing the same browser action",
        ],
        subtype="repeated_action_loop",
    )


def _classify_playwright_file_chooser(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("filechooser", "file chooser", "setinputfiles", "set input files", "upload", "input[type=file]")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_file_chooser",
        0.84,
        [f"file-upload marker found: {marker}" for marker in found[:3]],
        [
            "ensure the file chooser is awaited before the click that opens it",
            "verify the input accepts files and the local file path exists",
            "avoid relying on hidden upload widgets without a stable trigger",
        ],
        subtype="upload",
    )


def _classify_playwright_download(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("download", "acceptdownloads", "saveas", "download path", "download event", "suggestedfilename")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_download",
        0.84,
        [f"download marker found: {marker}" for marker in found[:3]],
        [
            "enable acceptDownloads in the browser context when needed",
            "wait for the download event around the user action",
            "persist the file with saveAs before the context closes",
        ],
        subtype="download_event",
    )


def _classify_playwright_popup(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("popup", "new page", "page.waitforevent('popup'", "target page, context or browser has been closed")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_popup",
        0.84,
        [f"popup/new-page marker found: {marker}" for marker in found[:3]],
        [
            "wrap the click and popup wait in the same Promise.all or equivalent",
            "continue extraction on the popup page instead of the opener",
            "record opener and popup URLs separately",
        ],
        subtype="popup_page",
    )


def _classify_playwright_service_worker_cache(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    markers = ("service worker", "serviceworker", "stale cache", "from service worker", "cache storage", "cached response")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "playwright_service_worker_cache",
        0.84,
        [f"service-worker/cache marker found: {marker}" for marker in found[:3]],
        [
            "separate cache/service-worker state from parser failures",
            "clear context storage or disable service workers for the regression when appropriate",
            "capture response source metadata such as fromServiceWorker/from cache",
        ],
        subtype="stale_cache",
    )


def _classify_selector_drift(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    missing_selectors = observations.get("missing_selectors", []) if isinstance(observations, Mapping) else []
    selector_markers = ("waiting for selector", "selector timeout", "locator(", "strict mode violation", "element not found")
    found = [marker for marker in selector_markers if marker in text]
    missing_fields = []
    expected_fields = artifact.get("expected", {}).get("required_fields", [])
    actual_fields = artifact.get("actual", {}).get("fields", {})
    if isinstance(expected_fields, list) and isinstance(actual_fields, Mapping):
        missing_fields = [field for field in expected_fields if field not in actual_fields or actual_fields.get(field) in (None, "", [])]
    if not found and not missing_selectors:
        return None
    if "password" in text or "captcha" in text or "too many requests" in text:
        return None
    evidence = [f"selector marker found: {marker}" for marker in found[:2]]
    if missing_selectors:
        evidence.append(f"missing selectors: {', '.join(map(str, missing_selectors[:5]))}")
    failed_action = observations.get("failed_action") if isinstance(observations, Mapping) else None
    if isinstance(failed_action, Mapping):
        api_name = failed_action.get("api_name")
        selector = failed_action.get("selector")
        snapshot = failed_action.get("after_snapshot") or failed_action.get("before_snapshot")
        action_bits = []
        if api_name:
            action_bits.append(str(api_name))
        if selector:
            action_bits.append(f"selector {selector}")
        if snapshot:
            action_bits.append(f"snapshot {snapshot}")
        if action_bits:
            evidence.append(f"failed action: {', '.join(action_bits)}")
    snapshot_refs = observations.get("snapshot_refs") if isinstance(observations, Mapping) else None
    if isinstance(snapshot_refs, list) and snapshot_refs:
        names = []
        for ref in snapshot_refs[:3]:
            if isinstance(ref, Mapping):
                names.append(str(ref.get("name") or ref.get("sha1") or "snapshot"))
        if names:
            evidence.append(f"snapshot refs available: {', '.join(names)}")
    dom_hints = observations.get("dom_hints") if isinstance(observations, Mapping) else None
    if isinstance(dom_hints, Mapping):
        candidates = dom_hints.get("candidate_selectors")
        if isinstance(candidates, list) and candidates:
            evidence.append(f"DOM candidates: {', '.join(map(str, candidates[:5]))}")
    if missing_fields:
        evidence.append(f"extraction fields missing after selector lookup: {', '.join(missing_fields)}")
    return _result(
        "selector_drift",
        0.86 if missing_selectors else 0.76,
        evidence,
        [
            "compare saved DOM snapshot with expected selectors",
            "replace brittle selectors with semantic or structural selectors",
            "add a fixture containing the changed DOM",
        ],
    )


def _classify_response_shape_change(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    expected_fields = artifact.get("expected", {}).get("required_fields", [])
    actual_fields = artifact.get("actual", {}).get("fields", {})
    evidence: list[str] = []
    if isinstance(expected_fields, list) and isinstance(actual_fields, Mapping):
        missing = [field for field in expected_fields if field not in actual_fields or actual_fields.get(field) in (None, "", [])]
        if missing:
            evidence.append(f"missing required fields: {', '.join(missing)}")
    if artifact.get("actual", {}).get("array_length") == 0:
        evidence.append("actual output array is empty")
    if "type changed" in text or "schema validation failed" in text:
        evidence.append("field type changed compared with expected schema")
    if not evidence:
        return None
    return _result(
        "response_shape_change",
        0.82 if len(evidence) > 1 else 0.72,
        evidence,
        [
            "compare expected schema with actual output",
            "update selectors or schema mapping",
            "add an empty-result guard before downstream processing",
        ],
    )


def _classify_toolchain_environment(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    observations = artifact.get("observations", {})
    if isinstance(observations, Mapping) and (
        observations.get("har_expected")
        or observations.get("har_path")
        or observations.get("har_error")
        or observations.get("har_loaded") is False
        or observations.get("route_registered") is not None
    ):
        return None
    if any(marker in text for marker in ("download", "saveas", "acceptdownloads", "suggestedfilename")):
        return None
    local_path_markers = ("filenotfounderror", "no such file or directory", "enoent")
    permission_markers = ("permission denied", "eacces")
    runtime_markers = (
        "pwsh",
        "powershell",
        "node is not recognized",
        "modulenotfounderror",
        "browser executable missing",
        "executable doesn't exist",
        "playwright install",
        "missing browser",
        "docker headless environment",
    )
    markers = local_path_markers + permission_markers + runtime_markers
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    if any(marker in text for marker in local_path_markers):
        subtype = "local_file_path_missing"
        confidence = 0.94
        fixes = [
            "create the missing local output/input directory before changing selectors or website logic",
            "resolve paths relative to the project root and add a preflight path check",
            "re-run after the local file path exists, then inspect any remaining page symptoms",
        ]
    elif any(marker in text for marker in permission_markers):
        subtype = "local_permission_denied"
        confidence = 0.9
        fixes = [
            "fix local file permissions or working-directory ownership first",
            "write outputs under an authorized project directory",
            "re-run before changing selectors or parser logic",
        ]
    else:
        subtype = "runtime_dependency_missing"
        confidence = 0.82
        fixes = ["verify local runtime versions", "check PATH and shell availability", "run the repo smoke test"]
    return _result(
        "toolchain_environment",
        confidence,
        [f"toolchain/environment marker found: {found[0]}"],
        fixes,
        can_auto_fix=True,
        subtype=subtype,
        evidence_level="confirmed",
    )


CLASSIFIERS = (
    _classify_cross_framework_adapter_hint,
    _classify_runtime_api_missing,
    _classify_header_normalization_evidence_gap,
    _classify_anti_bot_risk,
    _classify_captcha_or_bot_wall,
    _classify_js_bundle_obfuscation,
    _classify_playwright_shadow_dom_locator,
    _classify_website_change,
    _classify_playwright_storage_state_context,
    _classify_playwright_route_mock_har,
    _classify_auth_expiry,
    _classify_rate_limit_or_soft_block,
    _classify_network_http_error,
    _classify_toolchain_environment,
    _classify_playwright_popup,
    _classify_playwright_browser_context_closed,
    _classify_playwright_execution_context_destroyed,
    _classify_cdp_websocket_disconnected,
    _classify_agent_repetition_loop,
    _classify_async_hydration_timing,
    _classify_playwright_strict_mode_violation,
    _classify_playwright_frame_locator,
    _classify_playwright_file_chooser,
    _classify_playwright_download,
    _classify_playwright_service_worker_cache,
    _classify_selector_drift,
    _classify_response_shape_change,
)


def classify_failure_artifact(artifact: Mapping[str, Any]) -> dict[str, Any]:
    text = _combined_text(artifact)
    results = [result for classifier in CLASSIFIERS if (result := classifier(artifact, text))]
    if not results:
        return _result(
            "unknown",
            0.0,
            ["no matching failure pattern found"],
            [
                "collect more evidence: html snapshot, network log, console log, expected schema, actual output",
                "open an issue with a sanitized failure artifact",
            ],
        )
    results.sort(key=lambda item: item["confidence"], reverse=True)
    best = results[0]
    if len(results) > 1:
        best["alternative_diagnoses"] = [
            {"failure_type": item["failure_type"], "confidence": item["confidence"]}
            for item in results[1:]
        ]
    return best
