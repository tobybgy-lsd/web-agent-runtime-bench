"""Rule-based failure classifier for web automation artifacts.

No LLM calls. No network. Pure local rule matching against structured evidence.
"""

from __future__ import annotations

import json
from typing import Any, Mapping


def _combined_text(artifact: Mapping[str, Any]) -> str:
    return json.dumps(artifact, ensure_ascii=False).lower()


def _result(
    failure_type: str,
    confidence: float,
    evidence: list[str],
    suggested_fix: list[str],
    can_auto_fix: bool = False,
    subtype: str | None = None,
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
    return result


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
    markers = ("captcha", "verify you are human", "are you human", "turnstile", "recaptcha", "cloudflare challenge", "just a moment")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "captcha_or_bot_wall",
        0.88 if len(found) > 1 else 0.72,
        [f"challenge marker found: {marker}" for marker in found[:4]],
        [
            "stop automation and request authorized/manual review",
            "record as blocked, not as selector drift",
            "do not add CAPTCHA bypass or anti-bot evasion logic",
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


def _classify_auth_expiry(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
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
                "do not add anti-bot evasion or CAPTCHA bypass logic",
            ],
            subtype=f"http_{status}" if status else "soft_block_page",
        )
    return None


def _classify_network_http_error(artifact: Mapping[str, Any], text: str) -> dict[str, Any] | None:
    status = artifact.get("error", {}).get("status_code") or artifact.get("observations", {}).get("status_code")
    if status in (401, 403, 429) or (isinstance(status, int) and status >= 500):
        subtype = f"http_{status}"
        evidence = [f"HTTP status code indicates transport/server failure: {status}"]
        if status == 429:
            evidence.append("rate-limit status detected")
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
    transport_markers = ("timeout waiting for response", '"network_error": "timeout"', "dns", "connection reset", "tls", "empty response")
    found = [marker for marker in transport_markers if marker in text]
    if not found:
        return None
    return _result(
        "network_http_error",
        0.86,
        [f"transport marker found: {found[0]}"],
        ["retry with backoff if authorized", "capture response metadata separately from parser errors"],
        subtype="transport_error",
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
    markers = ("pwsh", "powershell", "node is not recognized", "modulenotfounderror", "permission denied", "no such file or directory")
    found = [marker for marker in markers if marker in text]
    if not found:
        return None
    return _result(
        "toolchain_environment",
        0.78,
        [f"toolchain/environment marker found: {found[0]}"],
        ["verify local runtime versions", "check PATH and shell availability", "run the repo smoke test"],
        can_auto_fix=True,
    )


CLASSIFIERS = (
    _classify_runtime_api_missing,
    _classify_captcha_or_bot_wall,
    _classify_js_bundle_obfuscation,
    _classify_auth_expiry,
    _classify_rate_limit_or_soft_block,
    _classify_network_http_error,
    _classify_toolchain_environment,
    _classify_async_hydration_timing,
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
