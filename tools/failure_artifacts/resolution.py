from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


FORBIDDEN_RESOLUTION_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "ip pool",
    "account pool",
    "绕过验证码",
    "绕过风控",
    "伪造指纹",
    "破解签名",
    "规避封禁",
)


PLAN_TEMPLATES: dict[str, dict[str, Any]] = {
    "selector_drift": {
        "fix_intent": "Update stale selector based on the current DOM.",
        "area": ["selectors", "DOM snapshot", "extraction assertions"],
        "disappear": ["missing selector", "locator resolved to 0 elements", "Timeout waiting for selector"],
        "appear": ["target element matched", "extracted field present", "updated selector matched"],
        "strategy": "Compare before/after evidence and confirm the stale selector evidence no longer appears.",
        "risk": "low",
    },
    "playwright_storage_state_context": {
        "fix_intent": "Restore or regenerate the authenticated browser context.",
        "area": ["storageState", "browser context", "auth preflight"],
        "disappear": ["302 redirect to login", "401 unauthorized", "session expired", "missing session cookie"],
        "appear": ["authenticated page reached", "session cookie retained", "authenticated route retained"],
        "strategy": "Verify the after run no longer redirects to login and reaches the authenticated page.",
        "risk": "medium",
    },
    "playwright_route_mock_har": {
        "fix_intent": "Register route/HAR before the first matching request and verify mock coverage.",
        "area": ["route setup", "HAR replay", "network assertions"],
        "disappear": ["live network leak", "HAR miss", "route registered after request"],
        "appear": ["route matched", "mock fulfilled", "no unexpected live request"],
        "strategy": "Compare route/HAR evidence and verify the request is handled by mock or HAR.",
        "risk": "medium",
    },
    "playwright_shadow_dom_locator": {
        "fix_intent": "Update locator strategy for the shadow DOM or custom element boundary.",
        "area": ["locator strategy", "component test hooks", "accessibility roles"],
        "disappear": ["ordinary locator failed", "target inside shadow DOM not reached"],
        "appear": ["target inner control matched", "locator action succeeded"],
        "strategy": "Verify the after run targets the intended inner control and the action succeeds.",
        "risk": "medium",
    },
    "playwright_strict_mode_violation": {
        "fix_intent": "Make the locator unique or target the intended element explicitly.",
        "area": ["locator", "role/test id", "selector scope"],
        "disappear": ["strict mode violation", "resolved to 2 elements", "multiple matches"],
        "appear": ["single locator match", "locator action succeeded"],
        "strategy": "Confirm the after run has one actionable locator target and no strict-mode error.",
        "risk": "low",
    },
    "playwright_download": {
        "fix_intent": "Persist the downloaded file and make it available to the next automation step.",
        "area": ["download handling", "file path", "acceptDownloads"],
        "disappear": ["download not saved", "file not available", "ENOENT"],
        "appear": ["download saved", "file exists", "next step can read file"],
        "strategy": "Verify the after run emits a saved file path and the file is readable.",
        "risk": "low",
    },
    "playwright_popup": {
        "fix_intent": "Handle the popup or new page explicitly before continuing the flow.",
        "area": ["popup handling", "page context", "next action"],
        "disappear": ["popup not handled", "new page ignored", "next step used wrong page"],
        "appear": ["popup captured", "new page selected", "next action used correct page"],
        "strategy": "Verify after evidence shows the new page or popup is captured before actions continue.",
        "risk": "medium",
    },
    "playwright_execution_context_destroyed": {
        "fix_intent": "Wait for navigation or page stability before evaluating in the page context.",
        "area": ["waiting logic", "navigation handling", "action sequencing"],
        "disappear": ["Execution context was destroyed", "navigation race"],
        "appear": ["navigation completed", "page stable", "action retried after navigation"],
        "strategy": "Verify the after run waits for navigation and no context-destroyed error appears.",
        "risk": "medium",
    },
    "network_http_error": {
        "fix_intent": "Fix the network, proxy, DNS, TLS, or timeout condition blocking page load.",
        "area": ["proxy", "DNS", "TLS", "network timeout"],
        "disappear": ["ERR_PROXY_CONNECTION_FAILED", "ERR_NAME_NOT_RESOLVED", "ERR_CERT", "network timeout"],
        "appear": ["page loaded", "HTTP response received", "transport error absent"],
        "strategy": "Verify the same transport error no longer appears in the after run.",
        "risk": "medium",
    },
    "website_change": {
        "fix_intent": "Update selector, endpoint, JSON path, or pagination logic according to the new site structure.",
        "area": ["site contract", "selectors", "network schema", "pagination"],
        "disappear": ["missing field", "old endpoint 404", "response shape mismatch"],
        "appear": ["required field present", "updated endpoint returns expected schema", "schema matched"],
        "strategy": "Verify after evidence matches the updated site contract without stale selectors or endpoints.",
        "risk": "medium",
    },
    "anti_bot_risk": {
        "fix_intent": "Do not bypass; confirm authorization and route to a compliant access path.",
        "area": ["authorization", "official API", "authorized export", "manual review"],
        "disappear": [],
        "appear": ["safe next action documented", "official API used", "authorized export used", "manual review completed", "collection stopped if authorization is unclear"],
        "strategy": "Verify the report stays compliance-oriented and does not suggest prohibited access-control defeat.",
        "risk": "high",
    },
    "insufficient_evidence": {
        "fix_intent": "Collect missing artifacts before attempting code changes.",
        "area": ["trace.zip", "error.log", "network.json", "user_description.txt"],
        "disappear": [],
        "appear": ["trace.zip", "error.log", "network.json", "user_description"],
        "strategy": "Verify that enough evidence exists to classify the next run before changing automation code.",
        "risk": "low",
    },
    "popup_or_overlay_blocking": {
        "fix_intent": "Handle the blocking overlay, modal, or popup before clicking the target.",
        "area": ["overlay handling", "popup handling", "click preconditions"],
        "disappear": ["click intercepted", "overlay intercepted", "element click intercepted"],
        "appear": ["overlay dismissed", "target click succeeded"],
        "strategy": "Verify the after run dismisses or waits out the blocker before clicking.",
        "risk": "medium",
    },
    "navigation_or_wait_timeout": {
        "fix_intent": "Replace brittle waits with a semantic ready or navigation condition.",
        "area": ["wait condition", "navigation lifecycle", "timeout budget"],
        "disappear": ["TimeoutException", "Navigation timeout", "waiting for selector"],
        "appear": ["ready condition observed", "navigation completed"],
        "strategy": "Verify the after run waits for the correct ready signal instead of timing out.",
        "risk": "medium",
    },
    "browser_driver_mismatch": {
        "fix_intent": "Align browser, driver, and runtime versions before editing automation logic.",
        "area": ["browser driver", "runtime install", "CI image"],
        "disappear": ["SessionNotCreatedException", "driver version mismatch"],
        "appear": ["browser session created", "driver version aligned"],
        "strategy": "Verify a fresh browser session can be created in the target environment.",
        "risk": "medium",
    },
    "selector_syntax_error": {
        "fix_intent": "Fix invalid CSS or XPath selector syntax.",
        "area": ["selector syntax", "locator construction", "selector tests"],
        "disappear": ["InvalidSelectorException", "invalid css or xpath"],
        "appear": ["selector parses", "locator resolves"],
        "strategy": "Verify the selector parses and resolves to the intended element.",
        "risk": "low",
    },
    "popup_or_new_page": {
        "fix_intent": "Switch to the correct window, tab, popup, or page before continuing.",
        "area": ["window handle", "popup lifecycle", "page selection"],
        "disappear": ["NoSuchWindowException", "window or tab closed"],
        "appear": ["target page selected", "window handle valid"],
        "strategy": "Verify the after run uses the correct page or window handle.",
        "risk": "medium",
    },
    "target_closed_or_page_crash": {
        "fix_intent": "Stabilize the browser target and avoid actions after page close or crash.",
        "area": ["browser lifecycle", "page crash logs", "resource limits"],
        "disappear": ["Target closed", "Page crashed"],
        "appear": ["target remains open", "page action completed"],
        "strategy": "Verify browser/page lifecycle logs show the target remains available.",
        "risk": "medium",
    },
    "cdp_protocol_error": {
        "fix_intent": "Separate CDP/runtime errors from page-level locator failures.",
        "area": ["CDP connection", "browser protocol", "runtime version"],
        "disappear": ["ProtocolError", "CDP protocol error"],
        "appear": ["protocol command succeeded", "browser transport stable"],
        "strategy": "Verify the after run no longer emits protocol transport errors.",
        "risk": "medium",
    },
    "fixture_or_mock_missing": {
        "fix_intent": "Restore the missing fixture or mock artifact and lock it with a regression check.",
        "area": ["fixture file", "mock path", "test data"],
        "disappear": ["fixture not found", "mock missing"],
        "appear": ["fixture loaded", "mock matched"],
        "strategy": "Verify the fixture or mock is resolved before the request/test step.",
        "risk": "low",
    },
    "environment_config_mismatch": {
        "fix_intent": "Fix environment config such as base URL before changing test logic.",
        "area": ["base URL", "environment variables", "CI config"],
        "disappear": ["baseUrl mismatch", "wrong environment"],
        "appear": ["base URL matches target", "environment config loaded"],
        "strategy": "Verify the report shows the expected base URL and target environment.",
        "risk": "low",
    },
    "browser_context_or_origin_policy": {
        "fix_intent": "Handle browser context or origin boundaries explicitly.",
        "area": ["origin policy", "context setup", "cross-origin flow"],
        "disappear": ["cross-origin blocked", "origin policy"],
        "appear": ["origin transition handled", "context boundary documented"],
        "strategy": "Verify the after run handles origin transitions without policy errors.",
        "risk": "medium",
    },
    "viewport_responsive_layout_mismatch": {
        "fix_intent": "Reproduce with the intended viewport and update responsive selectors.",
        "area": ["viewport", "responsive layout", "selector scope"],
        "disappear": ["viewport mismatch", "element hidden by responsive layout"],
        "appear": ["viewport matches", "responsive target visible"],
        "strategy": "Verify the after run uses the expected viewport and the element is visible.",
        "risk": "low",
    },
}


ALIASES = {
    "download_not_saved": "playwright_download",
    "popup_or_new_page": "playwright_popup",
    "execution_context_destroyed": "playwright_execution_context_destroyed",
    "strict_mode_violation": "playwright_strict_mode_violation",
}


def generate_fix_plan(diagnosis: Mapping[str, Any], evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    failure_type = str(diagnosis.get("failure_type") or diagnosis.get("technical_category") or "insufficient_evidence")
    failure_type = ALIASES.get(failure_type, failure_type)
    template = PLAN_TEMPLATES.get(failure_type, PLAN_TEMPLATES["insufficient_evidence"])
    subtype = diagnosis.get("subtype") or ""
    diagnosis_id = str(diagnosis.get("diagnosis_id") or diagnosis.get("run_id") or f"FD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    plan = {
        "schema_version": "fix_plan/v1",
        "diagnosis_id": diagnosis_id,
        "failure_type": failure_type,
        "technical_category": str(diagnosis.get("technical_category") or failure_type),
        "subtype": subtype,
        "failure_layer": str(diagnosis.get("failure_layer") or _failure_layer_for(failure_type)),
        "root_cause": subtype or failure_type,
        "fix_intent": template["fix_intent"],
        "recommended_change_area": list(template["area"]),
        "expected_evidence_to_disappear": list(template["disappear"]),
        "expected_evidence_to_appear": list(template["appear"]),
        "verification_strategy": template["strategy"],
        "risk": template["risk"],
        "safe_next_action": True,
        "forbidden_actions": ["access-control defeat", "challenge automation", "credential extraction", "unauthorized collection"],
    }
    if isinstance(diagnosis.get("repair_order"), list):
        plan["repair_order"] = list(diagnosis.get("repair_order", []))
    if isinstance(diagnosis.get("secondary_failures"), list):
        plan["secondary_failures"] = list(diagnosis.get("secondary_failures", []))
    if isinstance(diagnosis.get("blocking_failure"), Mapping):
        plan["blocking_failure"] = dict(diagnosis.get("blocking_failure", {}))
    return plan


def verify_resolution(
    before_diagnosis: Mapping[str, Any],
    before_evidence: Mapping[str, Any],
    after_diagnosis: Mapping[str, Any],
    after_evidence: Mapping[str, Any],
    fix_plan: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    before = _summary(before_diagnosis)
    after = _summary(after_diagnosis)
    plan = fix_plan or generate_fix_plan(before_diagnosis)
    before_type = before["failure_type"]
    after_type = after["failure_type"]
    before_text = _evidence_text(before_diagnosis, before_evidence)
    after_text = _evidence_text(after_diagnosis, after_evidence)
    disappear = [str(item) for item in plan.get("expected_evidence_to_disappear", [])]
    appear = [str(item) for item in plan.get("expected_evidence_to_appear", [])]

    if before_type == "anti_bot_risk":
        compliant_markers = ("official api", "authorized export", "manual review", "collection stopped", "authorization confirmed")
        if any(marker in after_text for marker in compliant_markers):
            status = "resolved_by_compliant_path"
            notes = ["anti-bot risk resolved only by compliant access path evidence"]
        else:
            status = "insufficient_evidence"
            notes = ["anti-bot risk cannot be marked resolved by bypass-style success; provide compliant path evidence"]
        return _verification_report(status, before, after, [], [], [] if after_type in {"none_detected", "unknown"} else [after_type], 0.72, False, notes)

    if _is_low_evidence(after_type, after_text):
        return _verification_report("insufficient_evidence", before, after, [], [], [], 0.45, False, ["after evidence is too thin to confirm resolution"])

    remaining = [item for item in disappear if _contains(after_text, item)]
    resolved = [item for item in disappear if _contains(before_text, item) and not _contains(after_text, item)]
    appeared = [item for item in appear if _contains(after_text, item)]

    if after_type == before_type and before_type not in {"unknown", "none_detected"}:
        if appeared and not remaining:
            return _verification_report("resolved", before, after, resolved + appeared, [], [], 0.82, True, ["same broad category appeared, but success evidence replaced the failure evidence"])
        return _verification_report("not_resolved", before, after, resolved, remaining or before["evidence"], [], 0.84, False, ["same failure type still appears after fix"])
    before_secondaries = _secondary_types(before_diagnosis)
    if after_type in before_secondaries and after_type != before_type:
        return _verification_report(
            "partially_resolved",
            before,
            after,
            resolved,
            remaining,
            [after_type],
            0.8,
            False,
            ["primary failure no longer appears, but a previously secondary/downstream failure remains"],
        )
    if after_type not in {"unknown", "none_detected", "insufficient_evidence"} and after_type != before_type:
        return _verification_report("changed_failure", before, after, resolved, remaining, [after_type], 0.78, False, ["original failure changed into a different failure"])
    if resolved or appeared or after_type in {"unknown", "none_detected"}:
        return _verification_report("resolved", before, after, resolved + appeared, remaining, [], 0.86, True, ["original failure evidence disappeared or success evidence appeared"])
    return _verification_report("insufficient_evidence", before, after, [], [], [], 0.5, False, ["unable to compare before and after evidence"])


def render_fix_plan_markdown(plan: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Fix Plan",
            "",
            "## Root Cause",
            "",
            str(plan.get("root_cause", "")),
            "",
            "## Fix Intent",
            "",
            str(plan.get("fix_intent", "")),
            "",
            "## Recommended Change Area",
            "",
            _bullets(plan.get("recommended_change_area", [])),
            "",
            "## Evidence Expected to Disappear",
            "",
            _bullets(plan.get("expected_evidence_to_disappear", [])) or "- none guaranteed",
            "",
            "## Evidence Expected to Appear",
            "",
            _bullets(plan.get("expected_evidence_to_appear", [])),
            "",
            "## Verification Strategy",
            "",
            str(plan.get("verification_strategy", "")),
            "",
            "## Safe Boundaries",
            "",
            "- This tool does not provide bypass guidance.",
            "- Use official API, authorized export, manual verification, reduced load, or stop unauthorized automation for platform-risk cases.",
        ]
    )


def render_verification_markdown(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Verification Report",
            "",
            "## Status",
            "",
            str(report.get("status", "")),
            "",
            "## Before",
            "",
            json.dumps(report.get("before", {}), ensure_ascii=False, indent=2),
            "",
            "## After",
            "",
            json.dumps(report.get("after", {}), ensure_ascii=False, indent=2),
            "",
            "## Resolved Evidence",
            "",
            _bullets(report.get("resolved_evidence", [])) or "- none",
            "",
            "## Remaining Evidence",
            "",
            _bullets(report.get("remaining_evidence", [])) or "- none",
            "",
            "## New Failures",
            "",
            _bullets(report.get("new_failures", [])) or "- none",
            "",
            "## Recommended Next Step",
            "",
            _next_step(report),
            "",
            "## Regression Case",
            "",
            "See `regression_case.json` when generated.",
        ]
    )


def _verification_report(status: str, before: dict[str, Any], after: dict[str, Any], resolved: list[str], remaining: list[str], new: list[str], confidence: float, regression: bool, notes: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "verification_report/v1",
        "status": status,
        "before": before,
        "after": after,
        "resolved_evidence": resolved,
        "remaining_evidence": remaining,
        "new_failures": new,
        "confidence": confidence,
        "regression_case_created": regression,
        "notes": notes,
    }


def _summary(diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    failure_type = str(diagnosis.get("failure_type") or diagnosis.get("technical_category") or "unknown")
    if failure_type == "unknown" and not diagnosis.get("evidence"):
        failure_type = "none_detected"
    return {
        "failure_type": failure_type,
        "technical_category": str(diagnosis.get("technical_category") or failure_type),
        "subtype": str(diagnosis.get("subtype") or ""),
        "evidence": list(diagnosis.get("evidence", [])) if isinstance(diagnosis.get("evidence", []), list) else [],
    }


def _secondary_types(diagnosis: Mapping[str, Any]) -> set[str]:
    values: set[str] = set()
    secondaries = diagnosis.get("secondary_failures")
    if isinstance(secondaries, list):
        for item in secondaries:
            if isinstance(item, Mapping):
                technical = item.get("technical_category") or item.get("failure_type")
                if technical:
                    values.add(str(technical))
    downstream = diagnosis.get("downstream_failures")
    if isinstance(downstream, list):
        for item in downstream:
            if isinstance(item, Mapping):
                technical = item.get("technical_category") or item.get("failure_type")
                if technical:
                    values.add(str(technical))
    return values


def _evidence_text(diagnosis: Mapping[str, Any], evidence: Mapping[str, Any]) -> str:
    parts = [json.dumps(diagnosis, ensure_ascii=False), json.dumps(evidence, ensure_ascii=False)]
    return "\n".join(parts).lower()


def _contains(text: str, marker: str) -> bool:
    marker = marker.lower()
    if not marker:
        return False
    return marker in text


def _is_low_evidence(failure_type: str, after_text: str) -> bool:
    if failure_type == "insufficient_evidence":
        return True
    if failure_type == "none_detected" and not any(marker in after_text for marker in ("matched", "extracted", "saved", "authenticated", "official api", "authorized")):
        return True
    return False


def _failure_layer_for(failure_type: str) -> str:
    if failure_type == "anti_bot_risk":
        return "anti_bot_risk"
    if failure_type == "website_change":
        return "website_change"
    if failure_type in {"network_http_error", "toolchain_environment", "cdp_websocket_disconnected"}:
        return "environment"
    if failure_type == "insufficient_evidence":
        return "insufficient_evidence"
    return "automation_engineering"


def _bullets(items: Any) -> str:
    if not isinstance(items, list):
        return ""
    return "\n".join(f"- {item}" for item in items)


def _next_step(report: Mapping[str, Any]) -> str:
    status = report.get("status")
    if status == "resolved":
        return "Create or update a regression case so this failure stays fixed."
    if status == "not_resolved":
        return "Revisit the fix plan; the original failure evidence is still present."
    if status == "changed_failure":
        return "Run diagnosis on the new failure and create a follow-up fix plan."
    if status == "resolved_by_compliant_path":
        return "Keep the compliant access path documented and do not add prohibited platform-risk handling."
    return "Collect more after-run evidence before claiming the fix worked."


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
