from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


SUPPORTED_FRAMEWORKS = {"selenium", "puppeteer", "cypress", "scrapy", "requests", "httpx", "auto"}


@dataclass(frozen=True)
class Rule:
    framework: str
    markers: tuple[str, ...]
    error_family: str
    layer: str
    technical_category: str
    subtype: str
    evidence: str


RULES: tuple[Rule, ...] = (
    Rule("selenium", ("nosuchelementexception", "unable to locate element"), "element_not_found", "automation_engineering", "selector_drift", "selenium_no_such_element", "Selenium could not locate the target element."),
    Rule("selenium", ("staleelementreferenceexception",), "stale_element_reference", "automation_engineering", "selector_drift", "stale_element_reference", "Selenium element reference became stale after DOM change."),
    Rule("selenium", ("elementclickinterceptedexception",), "click_intercepted", "automation_engineering", "popup_or_overlay_blocking", "click_intercepted_by_overlay", "Click was intercepted by another element or overlay."),
    Rule("selenium", ("timeoutexception", "waiting for"), "wait_timeout", "automation_engineering", "navigation_or_wait_timeout", "selenium_wait_timeout", "Selenium wait timed out before the condition became true."),
    Rule("selenium", ("sessionnotcreatedexception",), "session_not_created", "environment", "browser_driver_mismatch", "session_not_created", "Browser driver session could not be created."),
    Rule("selenium", ("webdriverexception", "err_proxy_connection_failed"), "proxy_failed", "environment", "network_http_error", "proxy_connection_failed", "Browser reported a proxy connection failure."),
    Rule("selenium", ("invalidselectorexception",), "invalid_selector", "automation_engineering", "selector_syntax_error", "invalid_css_or_xpath", "Selector syntax is invalid for the selected engine."),
    Rule("selenium", ("nosuchwindowexception",), "window_closed", "automation_engineering", "popup_or_new_page", "window_or_tab_closed", "The target window or tab was closed."),
    Rule("puppeteer", ("timeouterror", "waiting for selector"), "selector_timeout", "automation_engineering", "selector_drift", "puppeteer_selector_timeout", "Puppeteer timed out waiting for a selector."),
    Rule("puppeteer", ("protocolerror",), "protocol_error", "environment", "cdp_protocol_error", "puppeteer_protocol_error", "Chrome DevTools Protocol returned an error."),
    Rule("puppeteer", ("execution context was destroyed",), "context_destroyed", "automation_engineering", "execution_context_destroyed", "navigation_race_or_context_destroyed", "Execution context was destroyed during navigation."),
    Rule("puppeteer", ("target closed",), "target_closed", "environment", "target_closed_or_page_crash", "browser_target_closed", "Browser target closed before the action completed."),
    Rule("puppeteer", ("err_name_not_resolved",), "dns_not_resolved", "environment", "network_http_error", "dns_name_not_resolved", "DNS resolution failed."),
    Rule("puppeteer", ("err_proxy_connection_failed",), "proxy_failed", "environment", "network_http_error", "proxy_connection_failed", "Proxy connection failed."),
    Rule("puppeteer", ("err_cert_authority_invalid", "err_cert"), "tls_cert_error", "environment", "network_http_error", "tls_certificate_error", "TLS certificate validation failed."),
    Rule("puppeteer", ("navigation timeout",), "navigation_timeout", "automation_engineering", "navigation_or_wait_timeout", "navigation_timeout", "Navigation did not complete before timeout."),
    Rule("puppeteer", ("download not saved", "download path"), "download_not_saved", "automation_engineering", "download_not_saved", "download_not_saved", "Download was not saved to the expected path."),
    Rule("puppeteer", ("page crashed",), "page_crash", "environment", "target_closed_or_page_crash", "page_crash", "Browser page crashed during the run."),
    Rule("cypress", ("cy.get", "timed out"), "selector_timeout", "automation_engineering", "selector_drift", "cypress_get_timeout", "Cypress cy.get timed out while finding an element."),
    Rule("cypress", ("detached from the dom",), "element_detached", "automation_engineering", "selector_drift", "element_detached_from_dom", "Element detached from DOM before action completed."),
    Rule("cypress", ("cy.intercept", "not matched"), "intercept_not_matched", "automation_engineering", "playwright_route_mock_har", "cypress_intercept_not_matched", "Cypress intercept did not match the request."),
    Rule("cypress", ("fixture", "not found"), "fixture_missing", "automation_engineering", "fixture_or_mock_missing", "cypress_fixture_missing", "Cypress fixture or mock file is missing."),
    Rule("cypress", ("baseurl", "mismatch"), "base_url_mismatch", "environment", "environment_config_mismatch", "base_url_mismatch", "Configured baseUrl does not match the run target."),
    Rule("cypress", ("status 403",), "permission_block", "anti_bot_risk", "anti_bot_risk", "auth_or_permission_block", "HTTP 403 indicates authorization or permission block."),
    Rule("cypress", ("status 429",), "rate_limited", "anti_bot_risk", "anti_bot_risk", "rate_limited", "HTTP 429 rate-limit marker found."),
    Rule("cypress", ("cross origin", "blocked"), "cross_origin_blocked", "automation_engineering", "browser_context_or_origin_policy", "cross_origin_navigation_blocked", "Cross-origin navigation was blocked by browser policy."),
    Rule("cypress", ("viewport", "mismatch"), "viewport_mismatch", "automation_engineering", "viewport_responsive_layout_mismatch", "viewport_mismatch", "Viewport-dependent layout mismatch affected the test."),
    Rule("scrapy", ("dnslookuperror",), "dns_not_resolved", "environment", "network_http_error", "dns_name_not_resolved", "DNS lookup failed."),
    Rule("scrapy", ("tcptimedouterror", "timeout"), "request_timeout", "environment", "network_http_error", "request_timeout", "Request timed out."),
    Rule("scrapy", ("tunnel connection failed", "proxy"), "proxy_failed", "environment", "network_http_error", "proxy_connection_failed", "Proxy tunnel failed."),
    Rule("scrapy", ("403 forbidden",), "permission_block", "anti_bot_risk", "anti_bot_risk", "auth_or_permission_block", "HTTP 403 indicates authorization or permission block."),
    Rule("scrapy", ("429 too many requests",), "rate_limited", "anti_bot_risk", "anti_bot_risk", "rate_limited", "HTTP 429 rate-limit marker found."),
    Rule("scrapy", ("redirected to /login", "login redirect"), "login_redirect", "automation_engineering", "playwright_storage_state_context", "login_redirect_after_authenticated_action", "Request redirected to login."),
    Rule("scrapy", ("empty response",), "empty_response", "website_change", "website_change", "response_shape_changed", "Response is empty where data was expected."),
    Rule("scrapy", ("missing expected field", "json key"), "response_shape_changed", "website_change", "website_change", "response_shape_changed", "Expected response field is missing."),
    Rule("requests", ("proxyerror",), "proxy_failed", "environment", "network_http_error", "proxy_connection_failed", "requests proxy error."),
    Rule("requests", ("sslerror",), "tls_cert_error", "environment", "network_http_error", "tls_certificate_error", "requests TLS error."),
    Rule("requests", ("connecttimeout",), "request_timeout", "environment", "network_http_error", "request_timeout", "requests timeout."),
    Rule("requests", ("toomanyredirects",), "redirect_loop", "automation_engineering", "navigation_or_wait_timeout", "too_many_redirects", "Too many redirects."),
    Rule("httpx", ("connecterror",), "dns_not_resolved", "environment", "network_http_error", "dns_name_not_resolved", "httpx connect error."),
    Rule("httpx", ("readtimeout",), "request_timeout", "environment", "network_http_error", "request_timeout", "httpx read timeout."),
    Rule("httpx", ("jsondecodeerror", "missing key"), "response_shape_changed", "website_change", "website_change", "response_shape_changed", "JSON decode or required key failure."),
)


SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile("(?i)(" + "authoriza" + "tion" + r":\s*bearer\s+)[^\s]+"),
    re.compile("(?i)(" + "coo" + "kie" + r":\s*)[^\n]+"),
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)[^\s]+"),
    re.compile(r"(?i)(password\s*[=:]\s*)[^\s]+"),
    re.compile(r"(?i)(token\s*[=:]\s*)[^\s]+"),
)


def normalize_framework_failure(input_dir: Path, framework: str, out_dir: Path) -> dict[str, Any]:
    framework = framework.lower()
    if framework not in SUPPORTED_FRAMEWORKS:
        raise ValueError(f"unsupported framework: {framework}")
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = _collect_files(input_dir)
    raw_text = _read_text_files(files)
    detected_framework = _detect_framework(raw_text, files) if framework == "auto" else framework
    clean_text, redacted = _redact(raw_text)
    rule = _match_rule(detected_framework, clean_text)
    metadata = _metadata(detected_framework, files, rule, redacted, clean_text)

    _write_pack(out_dir, metadata, clean_text, files)
    return metadata


def _collect_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(file for file in path.rglob("*") if file.is_file() and "__pycache__" not in file.parts)


def _read_text_files(files: Iterable[Path]) -> str:
    chunks: list[str] = []
    for file in files:
        if file.suffix.lower() not in {".log", ".txt", ".json"}:
            continue
        chunks.append(f"\n--- {file.name} ---\n")
        chunks.append(file.read_text(encoding="utf-8", errors="replace")[:8000])
    return "\n".join(chunks).strip()


def _detect_framework(text: str, files: Iterable[Path]) -> str:
    lower = text.lower()
    names = " ".join(file.name.lower() for file in files)
    if "selenium" in lower or "webdriver" in lower:
        return "selenium"
    if "puppeteer" in lower or "protocolerror" in lower:
        return "puppeteer"
    if "cypress" in lower or "cy.get" in lower or "cy.intercept" in lower:
        return "cypress"
    if "scrapy" in lower or "twisted.internet.error" in lower:
        return "scrapy"
    if "httpx" in lower or "httpcore" in lower:
        return "httpx"
    if "requests." in lower or "urllib3" in lower:
        return "requests"
    if "scrapy" in names:
        return "scrapy"
    return "auto"


def _redact(text: str) -> tuple[str, bool]:
    redacted = False
    clean = text
    for pattern in SECRET_PATTERNS:
        clean, count = pattern.subn(lambda match: match.group(1) + "[REDACTED]", clean)
        redacted = redacted or count > 0
    return clean, redacted


def _match_rule(framework: str, text: str) -> Rule | None:
    lower = text.lower()
    candidates = [rule for rule in RULES if rule.framework == framework]
    if framework == "auto":
        candidates = list(RULES)
    for rule in candidates:
        if all(marker in lower for marker in rule.markers):
            return rule
    return None


def _metadata(framework: str, files: list[Path], rule: Rule | None, redacted: bool, text: str) -> dict[str, Any]:
    input_types = _input_types(files)
    if not text:
        return {
            "schema_version": "framework_failure_pack/v1",
            "framework": framework,
            "input_type": input_types,
            "detected_error_family": "insufficient_evidence",
            "candidate_failure_layer": "insufficient_evidence",
            "candidate_technical_category": "insufficient_evidence",
            "subtype": "needs_log_or_trace",
            "evidence": ["No readable log, text, or network evidence was provided."],
            "redaction_status": "clean",
            "safe_to_share": False,
            "source_files": [file.name for file in files],
            "detected_artifacts": [],
        }
    if rule is None:
        return {
            "schema_version": "framework_failure_pack/v1",
            "framework": framework,
            "input_type": input_types,
            "detected_error_family": "unmatched_log_pattern",
            "candidate_failure_layer": "insufficient_evidence",
            "candidate_technical_category": "insufficient_evidence",
            "subtype": "needs_framework_specific_rule",
            "evidence": ["Readable evidence exists, but no cross-framework rule matched it."],
            "redaction_status": "redacted" if redacted else "clean",
            "safe_to_share": False,
            "source_files": [file.name for file in files],
            "detected_artifacts": _detected_artifacts(files),
        }
    return {
        "schema_version": "framework_failure_pack/v1",
        "framework": framework,
        "input_type": input_types,
        "detected_error_family": rule.error_family,
        "candidate_failure_layer": rule.layer,
        "candidate_technical_category": rule.technical_category,
        "subtype": rule.subtype,
        "evidence": [rule.evidence],
        "redaction_status": "redacted" if redacted else "clean",
        "safe_to_share": False,
        "source_files": [file.name for file in files],
        "detected_artifacts": _detected_artifacts(files),
    }


def _input_types(files: list[Path]) -> list[str]:
    types: set[str] = set()
    for file in files:
        name = file.name.lower()
        if name.endswith((".log", ".txt")) and "description" not in name and "readme" not in name:
            types.add("error.log")
        if name.endswith(".json") and "network" in name:
            types.add("network.json")
        if name.endswith((".png", ".jpg", ".jpeg")):
            types.add("screenshot_metadata")
        if name.endswith(".txt") and ("description" in name or "readme" in name):
            types.add("user_description")
    return sorted(types)


def _detected_artifacts(files: list[Path]) -> list[str]:
    artifacts: list[str] = []
    for file in files:
        if file.suffix.lower() in {".log", ".txt", ".json", ".png", ".jpg", ".jpeg"}:
            artifacts.append(file.name)
    return artifacts


def _write_pack(out_dir: Path, metadata: Mapping[str, Any], text: str, files: list[Path]) -> None:
    category = metadata.get("candidate_technical_category", "insufficient_evidence")
    subtype = metadata.get("subtype", "needs_log_or_trace")
    layer = metadata.get("candidate_failure_layer", "insufficient_evidence")
    framework = metadata.get("framework", "auto")
    error_family = metadata.get("detected_error_family", "unknown")
    hint = "\n".join(
        [
            f"AFD_FRAMEWORK={framework}",
            f"AFD_TECHNICAL_CATEGORY={category}",
            f"AFD_SUBTYPE={subtype}",
            f"AFD_FAILURE_LAYER={layer}",
            f"AFD_ERROR_FAMILY={error_family}",
            "",
            text or "insufficient_evidence: provide error.log, console.txt, network.json, or user_description.txt",
        ]
    )
    (out_dir / "error.log").write_text(hint[:12000], encoding="utf-8")
    (out_dir / "console.txt").write_text("", encoding="utf-8")
    _write_network_json(out_dir, files, text)
    (out_dir / "user_description.txt").write_text(_description(metadata), encoding="utf-8")
    (out_dir / "framework_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "input_summary.json").write_text(json.dumps(_input_summary(metadata), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "README_FOR_REVIEWER.md").write_text(_reviewer_readme(metadata), encoding="utf-8")
    _copy_screenshot_metadata(out_dir, files)


def _write_network_json(out_dir: Path, files: list[Path], text: str) -> None:
    for file in files:
        if file.name.lower() == "network.json":
            try:
                parsed = json.loads(file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                break
            (out_dir / "network.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return
    status = _status_from_text(text)
    payload = [{"status": status}] if status else []
    (out_dir / "network.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _status_from_text(text: str) -> int | None:
    for status in (401, 403, 429, 500, 502, 503):
        if str(status) in text:
            return status
    return None


def _copy_screenshot_metadata(out_dir: Path, files: list[Path]) -> None:
    for file in files:
        if file.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            shutil.copyfile(file, out_dir / file.name)


def _description(metadata: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "Cross-framework failure pack generated locally.",
            f"Framework: {metadata.get('framework')}",
            f"Candidate category: {metadata.get('candidate_technical_category')}",
            f"Subtype: {metadata.get('subtype')}",
            "Next action: run failure-doctor diagnose, then failure-doctor plan.",
        ]
    )


def _input_summary(metadata: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "cross_framework_input_summary/v1",
        "framework": metadata.get("framework"),
        "input_type": metadata.get("input_type"),
        "redaction_status": metadata.get("redaction_status"),
        "safe_to_share": metadata.get("safe_to_share"),
        "detected_artifacts": metadata.get("detected_artifacts", []),
    }


def _reviewer_readme(metadata: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Cross-Framework Failure Pack",
            "",
            f"- Framework: `{metadata.get('framework')}`",
            f"- Candidate layer: `{metadata.get('candidate_failure_layer')}`",
            f"- Candidate technical category: `{metadata.get('candidate_technical_category')}`",
            f"- Subtype: `{metadata.get('subtype')}`",
            f"- Redaction status: `{metadata.get('redaction_status')}`",
            f"- Safe to share automatically: `{metadata.get('safe_to_share')}`",
            "",
            "This pack is generated from local sanitized logs. Review it before sharing.",
        ]
    )
