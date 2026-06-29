"""Adapters that convert common tool outputs into failure artifacts.

These adapters are intentionally lightweight and local-only. They do not replay
requests or inspect real sites; they normalize already-captured evidence.
"""

from __future__ import annotations

import json
import re
import fnmatch
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZipFile

SCHEMA_VERSION = "failure-artifact/v1"


def artifact_from_playwright_trace(trace_zip: Path | str, *, run_id: str | None = None) -> dict[str, Any]:
    path = Path(trace_zip)
    console_messages: list[str] = []
    network_events: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    snapshot_refs: list[dict[str, str]] = []
    text_resources: dict[str, str] = {}
    html_snapshot = ""
    status_code: int | None = None
    url = ""
    if not path.exists():
        raise FileNotFoundError(f"trace.zip not found: {path}")

    with ZipFile(path) as archive:
        for name in archive.namelist():
            lower = name.lower()
            data = archive.read(name)
            text = data.decode("utf-8", errors="replace")
            if _is_text_resource(lower):
                text_resources[name] = text[:5000]
            status_code = _extract_status(text) or status_code
            for record in _parse_json_records(text):
                records.append(record)
                for message in _extract_record_messages(record):
                    _append_unique(console_messages, message, limit=20)
                event = _extract_network_event(record)
                if event:
                    if event not in network_events:
                        network_events.append(event)
                    status_code = _as_int(event.get("status")) or status_code
                    url = str(event.get("url") or url)
                snapshot_ref = _extract_snapshot_ref(record)
                if snapshot_ref and snapshot_ref not in snapshot_refs:
                    snapshot_refs.append(snapshot_ref)

            if "console" in lower or lower.endswith(".log"):
                _append_unique(console_messages, text, limit=20)
            elif lower.endswith((".html", ".dom")) or "dom" in lower:
                html_snapshot += text[:5000]
            elif "network" in lower or lower.endswith(".json"):
                parsed = _loads_json_or_none(text)
                if isinstance(parsed, dict):
                    status_code = _as_int(parsed.get("status") or parsed.get("status_code")) or status_code
                    url = str(parsed.get("url") or url)
                else:
                    status_code = _extract_status(text) or status_code

    action_events, failed_action, action_stack = _extract_action_observations(records)
    exception_details = _extract_exception_details(records)
    storage_context = _extract_storage_context_observations(records)
    route_mock_har = _extract_route_mock_har_observations(records)
    shadow_dom = _extract_shadow_dom_observations(records)
    error_stack = action_stack or _first_exception_stack(exception_details)
    missing_selectors = [failed_action["selector"]] if failed_action.get("selector") else []
    snapshot_excerpts = _link_snapshot_excerpts(snapshot_refs, text_resources)
    dom_hint_source = " ".join(item.get("excerpt", "") for item in snapshot_excerpts) or html_snapshot
    shadow_dom = _enrich_shadow_dom_from_html(shadow_dom, dom_hint_source)
    dom_hints = _extract_dom_hints(dom_hint_source, missing_selectors)

    return _base_artifact(
        run_id=run_id,
        tool="playwright",
        summary="Collected from Playwright trace.zip",
        status_code=status_code,
        error_message=" ".join(console_messages)[:500],
        error_stack=error_stack,
        artifacts={"trace": path.name, "html_snapshot": "snapshot.html"} if html_snapshot else {"trace": path.name},
        observations={
            "source_adapter": "playwright_trace",
            "url": url,
            "console_messages": console_messages,
            "network_events": network_events[:20],
            "action_events": action_events[:20],
            "failed_action": failed_action,
            "exception_details": exception_details[:20],
            "snapshot_refs": snapshot_refs[:20],
            "snapshot_excerpts": snapshot_excerpts[:20],
            "missing_selectors": missing_selectors,
            "dom_hints": dom_hints,
            "html_excerpt": html_snapshot[:1000],
            **storage_context,
            **route_mock_har,
            **shadow_dom,
        },
    )


def artifact_from_scrapy_run(log_path: Path | str, response_path: Path | str | None = None, *, run_id: str | None = None) -> dict[str, Any]:
    log = Path(log_path)
    if not log.exists():
        raise FileNotFoundError(f"Scrapy log not found: {log}")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    status_code = _extract_status(log_text)
    response_text = ""
    artifacts = {"error_log": log.name}
    if response_path:
        response = Path(response_path)
        if response.exists():
            response_text = response.read_text(encoding="utf-8", errors="replace")[:5000]
            artifacts["html_snapshot"] = response.name
    return _base_artifact(
        run_id=run_id,
        tool="scrapy",
        summary="Collected from Scrapy log and optional response snapshot",
        status_code=status_code,
        error_message=log_text[:500],
        artifacts=artifacts,
        observations={
            "source_adapter": "scrapy",
            "log_excerpt": log_text[:1000],
            "body_text": response_text[:1000],
        },
    )


def artifact_from_requests_run(input_path: Path | str, *, run_id: str | None = None) -> dict[str, Any]:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"requests capture not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    parsed = _loads_json_or_none(text)
    if isinstance(parsed, dict):
        status_code = _as_int(parsed.get("status_code") or parsed.get("status"))
        body = str(parsed.get("body") or parsed.get("text") or "")
        url = str(parsed.get("url") or "")
        error_message = str(parsed.get("error") or body[:500])
    else:
        status_code = _extract_status(text)
        body = text
        url = ""
        error_message = text[:500]
    return _base_artifact(
        run_id=run_id,
        tool="requests",
        summary="Collected from requests capture",
        status_code=status_code,
        error_message=error_message,
        artifacts={"network_log": path.name},
        observations={
            "source_adapter": "requests",
            "url": url,
            "body_text": body[:1000],
        },
    )


def _base_artifact(
    *,
    run_id: str | None,
    tool: str,
    summary: str,
    status_code: int | None,
    error_message: str,
    artifacts: dict[str, str],
    observations: dict[str, Any],
    error_stack: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or f"{tool}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "tool": tool,
        "target_type": "sanitized_real_failure",
        "summary": summary,
        "error": {"message": error_message, "stack": error_stack, "status_code": status_code},
        "artifacts": artifacts,
        "observations": observations,
        "expected": {"required_fields": []},
        "actual": {"fields": {}, "array_length": None},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
            "redaction_notes": "Generated from local captured tool output; review before sharing.",
        },
    }


def _loads_json_or_none(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _parse_json_records(text: str) -> list[dict[str, Any]]:
    parsed = _loads_json_or_none(text)
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]

    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith(("{", "[")):
            continue
        parsed_line = _loads_json_or_none(line)
        if isinstance(parsed_line, dict):
            records.append(parsed_line)
        elif isinstance(parsed_line, list):
            records.extend(item for item in parsed_line if isinstance(item, dict))
    return records


def _extract_record_messages(record: dict[str, Any]) -> list[str]:
    record_type = str(record.get("type") or record.get("method") or "").lower()
    params = record.get("params") if isinstance(record.get("params"), dict) else {}
    candidates: list[Any] = []

    if any(marker in record_type for marker in ("console", "error", "exception")):
        candidates.extend([record.get("message"), record.get("text"), record.get("error"), record.get("stack")])
        candidates.extend([params.get("message"), params.get("text"), params.get("error"), params.get("stack")])

    if "message" in record and isinstance(record.get("message"), dict):
        candidates.append(record["message"].get("text"))
    if "error" in record:
        candidates.append(record.get("error"))
    if "exceptionDetails" in params:
        candidates.append(params.get("exceptionDetails"))

    messages: list[str] = []
    for candidate in candidates:
        message = _coerce_message_text(candidate)
        if message:
            messages.append(message)
    return messages


def _coerce_message_text(value: Any) -> str:
    if isinstance(value, str):
        return value[:500]
    if isinstance(value, dict):
        for key in ("text", "message", "description", "stack", "value"):
            message = _coerce_message_text(value.get(key))
            if message:
                return message
    return ""


def _extract_network_event(record: dict[str, Any]) -> dict[str, Any] | None:
    record_type = str(record.get("type") or record.get("method") or "").lower()
    params = record.get("params") if isinstance(record.get("params"), dict) else {}
    response = _first_dict(record.get("response"), params.get("response"))
    request = _first_dict(record.get("request"), params.get("request"), response.get("request") if response else None)

    status = _as_int(
        record.get("status")
        or record.get("status_code")
        or record.get("statusCode")
        or (response or {}).get("status")
        or (response or {}).get("status_code")
        or (response or {}).get("statusCode")
    )
    url = str(
        record.get("url")
        or params.get("url")
        or (response or {}).get("url")
        or (request or {}).get("url")
        or ""
    )
    method = str((request or {}).get("method") or record.get("requestMethod") or params.get("requestMethod") or "")
    from_service_worker = bool(
        record.get("fromServiceWorker")
        or params.get("fromServiceWorker")
        or (response or {}).get("fromServiceWorker")
        or (request or {}).get("fromServiceWorker")
    )
    from_cache = bool(
        record.get("fromCache")
        or params.get("fromCache")
        or (response or {}).get("fromCache")
        or (request or {}).get("fromCache")
    )

    looks_network_like = bool(status or url) and (
        "network" in record_type
        or "request" in record
        or "response" in record
        or "request" in params
        or "response" in params
    )
    if not looks_network_like:
        return None

    event: dict[str, Any] = {}
    if method:
        event["method"] = method
    if url:
        event["url"] = url
    if status is not None:
        event["status"] = status
    if from_service_worker:
        event["from_service_worker"] = True
        event["source"] = "service worker"
    if from_cache:
        event["from_cache"] = True
        event["cache"] = "cached response"
    return event if event else None


def _extract_action_observations(records: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, str], str]:
    actions_by_call_id: dict[str, dict[str, str]] = {}
    action_events: list[dict[str, str]] = []
    failed_action: dict[str, str] = {}
    error_stack = ""

    for record in records:
        record_type = str(record.get("type") or "").lower()
        call_id = str(record.get("callId") or record.get("call_id") or "")
        if record_type == "before" and call_id:
            params = record.get("params") if isinstance(record.get("params"), dict) else {}
            action = {
                "call_id": call_id,
                "api_name": str(record.get("apiName") or record.get("api_name") or ""),
            }
            selector = params.get("selector") or record.get("selector")
            if selector:
                action["selector"] = str(selector)
            event_name = params.get("event") or record.get("event")
            if event_name:
                action["event"] = str(event_name)
            url = params.get("url") or record.get("url")
            if url:
                action["url"] = str(url)
            locator = params.get("locator") or params.get("selectorOrLocator") or record.get("locator")
            if locator:
                action["locator"] = str(locator)
            before_snapshot = record.get("beforeSnapshot") or record.get("snapshot") or record.get("snapshotName")
            if before_snapshot:
                action["before_snapshot"] = str(before_snapshot)
            actions_by_call_id[call_id] = action
            action_events.append(dict(action))
        elif record_type == "after" and call_id:
            action = dict(actions_by_call_id.get(call_id, {"call_id": call_id}))
            after_snapshot = record.get("afterSnapshot") or record.get("snapshot") or record.get("snapshotName")
            if after_snapshot:
                action["after_snapshot"] = str(after_snapshot)
            error = record.get("error")
            error_message = _coerce_message_text(error)
            if error_message:
                action["error"] = error_message
                failed_action = action
            if isinstance(error, dict):
                error_stack = _coerce_stack_text(error.get("stack")) or error_stack
            if action not in action_events:
                action_events.append(action)

    return action_events, failed_action, error_stack


def _extract_exception_details(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    details: list[dict[str, str]] = []
    for record in records:
        params = record.get("params") if isinstance(record.get("params"), dict) else {}
        raw_detail = params.get("exceptionDetails") or record.get("exceptionDetails")
        if not isinstance(raw_detail, dict):
            continue
        exception = raw_detail.get("exception") if isinstance(raw_detail.get("exception"), dict) else {}
        message = (
            _coerce_message_text(exception.get("description"))
            or _coerce_message_text(raw_detail.get("text"))
            or _coerce_message_text(raw_detail)
        )
        stack = _coerce_stack_text(raw_detail.get("stackTrace")) or _coerce_stack_text(raw_detail.get("stack"))
        detail: dict[str, str] = {}
        if message:
            detail["message"] = message
        if stack:
            detail["stack"] = stack
        if detail and detail not in details:
            details.append(detail)
    return details


def _extract_storage_context_observations(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Infer storageState and auth-context signals from Playwright trace records."""
    observations: dict[str, Any] = {}
    field_map = {
        "storageStateExpected": "storage_state_expected",
        "storageStateLoaded": "storage_state_loaded",
        "missingCookieNames": "missing_cookie_names",
        "cookieDomain": "cookie_domain",
        "currentHost": "current_host",
        "contextRecreated": "context_recreated",
        "newContextStorageState": "new_context_storage_state",
        "previousAuthenticatedContext": "previous_authenticated_context",
        "expectedLocalStorageKeys": "expected_local_storage_keys",
        "missingLocalStorageKeys": "missing_local_storage_keys",
        "baseURL": "base_url",
        "storageStateOrigin": "storage_state_origin",
        "finalUrl": "final_url",
        "redirectedToLogin": "redirected_to_login",
    }
    for record in records:
        for source in _candidate_sources(record):
            for raw_key, normalized_key in field_map.items():
                if raw_key in source and normalized_key not in observations:
                    observations[normalized_key] = source[raw_key]
                elif normalized_key in source and normalized_key not in observations:
                    observations[normalized_key] = source[normalized_key]

    if "storage_state_expected" in observations or "storage_state_loaded" in observations:
        return observations

    auth_path_markers = ("/login", "/signin", "/sign-in", "/auth", "/account/login", "/session/new")

    def is_auth_url(value: str) -> bool:
        lowered = value.lower()
        return any(marker in lowered for marker in auth_path_markers)

    new_page_seen = False
    new_page_has_storage_state = False
    auth_redirect_url = ""
    auth_status_seen = False

    for record in records:
        record_type = str(record.get("type") or "").lower()
        method = str(record.get("method") or "").lower()
        params = record.get("params") if isinstance(record.get("params"), dict) else {}
        api_name = str(record.get("apiName") or record.get("api_name") or "").lower()

        if record_type == "before" and "context.newpage" in api_name:
            new_page_seen = True
            if "storageState" in params or "storage_state" in params:
                new_page_has_storage_state = True

        if record_type == "event" and "network.responsereceived" in method:
            response = params.get("response") if isinstance(params.get("response"), dict) else {}
            headers = response.get("headers") if isinstance(response.get("headers"), dict) else {}
            response_url = str(response.get("url") or "")
            status = _as_int(response.get("status"))
            location = str(headers.get("location") or headers.get("Location") or "")
            if is_auth_url(response_url) or (status in (301, 302, 307, 308) and is_auth_url(location)):
                auth_redirect_url = location or response_url
                auth_status_seen = True
            if status == 401:
                auth_status_seen = True

        if record_type == "event" and "page.framenavigated" in method:
            frame = params.get("frame") if isinstance(params.get("frame"), dict) else {}
            frame_url = str(frame.get("url") or "")
            if is_auth_url(frame_url):
                auth_redirect_url = frame_url
                auth_status_seen = True

        if record_type == "event" and "runtime.consoleapicalled" in method:
            args = params.get("args") if isinstance(params.get("args"), list) else []
            for arg in args:
                if not isinstance(arg, dict):
                    continue
                value = str(arg.get("value") or "").lower()
                if any(marker in value for marker in ("not authenticated", "session expired", "unauthorized", "please log in")):
                    auth_status_seen = True

        if record_type == "after" and "goto" in api_name:
            error = record.get("error") if isinstance(record.get("error"), dict) else {}
            error_message = str(error.get("message") or "").lower()
            if is_auth_url(error_message) or "redirect" in error_message:
                auth_status_seen = True

    if auth_status_seen:
        if new_page_seen and not new_page_has_storage_state:
            observations["storage_state_expected"] = True
            observations["storage_state_loaded"] = False
            observations.setdefault("final_url", auth_redirect_url)
        else:
            observations.setdefault("final_url", auth_redirect_url)
            observations.setdefault("redirected_to_login", True)
    return observations


def _extract_route_mock_har_observations(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Infer route/mock/HAR signals from Playwright trace records."""
    observations: dict[str, Any] = {}
    field_map = {
        "routeRegistered": "route_registered",
        "routePattern": "route_pattern",
        "requestUrl": "request_url",
        "routeMatched": "route_matched",
        "liveNetworkRequest": "live_network_request",
        "routeRegisteredAfterRequest": "route_registered_after_request",
        "firstRequestUrl": "first_request_url",
        "routeRegisteredAtMs": "route_registered_at_ms",
        "firstRequestAtMs": "first_request_at_ms",
        "harExpected": "har_expected",
        "harLoaded": "har_loaded",
        "harPath": "har_path",
        "harError": "har_error",
        "harNotFoundPolicy": "har_not_found_policy",
        "harMissUrl": "har_miss_url",
        "mockResponseFulfilled": "mock_response_fulfilled",
        "mockStatus": "mock_status",
        "expectedResponseFields": "expected_response_fields",
        "actualResponseFields": "actual_response_fields",
        "mockResponseShapeMismatch": "mock_response_shape_mismatch",
    }
    for record in records:
        for source in _candidate_sources(record):
            for raw_key, normalized_key in field_map.items():
                if raw_key in source and normalized_key not in observations:
                    observations[normalized_key] = source[raw_key]
                elif normalized_key in source and normalized_key not in observations:
                    observations[normalized_key] = source[normalized_key]

    if "route_registered" in observations or "har_expected" in observations:
        return observations

    route_patterns: list[str] = []
    route_registered_at_ms: float | None = None
    first_request_url = ""
    first_request_at_ms: float | None = None
    live_network_urls: list[str] = []
    har_load_failed = False

    for record in records:
        record_type = str(record.get("type") or "").lower()
        method = str(record.get("method") or "").lower()
        params = record.get("params") if isinstance(record.get("params"), dict) else {}
        api_name = str(record.get("apiName") or record.get("api_name") or "").lower()
        start_time = _as_float(record.get("startTime") or record.get("start_time"))

        if record_type == "before" and "page.route" in api_name and "fromhar" not in api_name:
            pattern = str(params.get("url") or params.get("pattern") or "")
            if pattern:
                route_patterns.append(pattern)
                observations["route_registered"] = True
                observations["route_pattern"] = pattern
                if start_time is not None and route_registered_at_ms is None:
                    route_registered_at_ms = start_time

        if record_type == "before" and "routefromhar" in api_name:
            har_path = str(params.get("har") or params.get("harPath") or "")
            observations["har_expected"] = True
            observations["har_loaded"] = True
            if har_path:
                observations["har_path"] = har_path
            observations["har_not_found_policy"] = str(params.get("notFound") or "abort")

        if record_type == "event" and "network.requestwillbesent" in method:
            request = params.get("request") if isinstance(params.get("request"), dict) else {}
            request_url = str(request.get("url") or "")
            request_time = _as_float(params.get("timestamp"))
            if request_url:
                if not first_request_url:
                    first_request_url = request_url
                    first_request_at_ms = request_time * 1000 if request_time is not None else None
                live_network_urls.append(request_url)

        if record_type == "event" and "network.loadingfailed" in method:
            error_text = str(params.get("errorText") or "").lower()
            if "file_not_found" in error_text or "err_file_not_found" in error_text:
                har_load_failed = True
                observations["har_loaded"] = False
                observations["har_error"] = params.get("errorText", "")

        if record_type == "after" and "route.fulfill" in api_name and record.get("error"):
            observations.setdefault("har_miss_url", first_request_url)

    if route_registered_at_ms is not None and first_request_at_ms is not None:
        if route_registered_at_ms > first_request_at_ms:
            observations["route_registered_after_request"] = True
            observations["first_request_url"] = first_request_url
            observations["route_registered_at_ms"] = route_registered_at_ms
            observations["first_request_at_ms"] = first_request_at_ms
        elif route_patterns and live_network_urls:
            for url in live_network_urls:
                matched = any(fnmatch.fnmatch(url, pattern.replace("**", "*")) for pattern in route_patterns)
                if not matched:
                    observations.setdefault("request_url", url)
                    observations["route_matched"] = False
                    observations["live_network_request"] = True
                    break
            else:
                observations["route_matched"] = True

    if har_load_failed:
        observations["har_loaded"] = False

    return observations


def _extract_shadow_dom_observations(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Infer shadow DOM signals from Playwright trace records."""
    observations: dict[str, Any] = {}
    field_map = {
        "shadowHost": "shadow_host",
        "shadowRootMode": "shadow_root_mode",
        "innerSelector": "inner_selector",
        "elementExistsInShadowDom": "element_exists_in_shadow_dom",
        "ordinaryLocatorFailed": "ordinary_locator_failed",
        "customElementTag": "custom_element_tag",
        "customElementDefined": "custom_element_defined",
        "customElementUpgraded": "custom_element_upgraded",
        "locatorTarget": "locator_target",
        "intendedInnerSelector": "intended_inner_selector",
        "hostLocatorClicked": "host_locator_clicked",
        "innerNodeNotTargeted": "inner_node_not_targeted",
        "testId": "testid",
        "testid": "testid",
        "testIdInsideShadowDom": "testid_inside_shadow_dom",
        "testidInsideShadowDom": "testid_inside_shadow_dom",
        "missingShadowStrategy": "missing_shadow_strategy",
    }
    for record in records:
        for source in _candidate_sources(record):
            for raw_key, normalized_key in field_map.items():
                if raw_key in source and normalized_key not in observations:
                    observations[normalized_key] = source[raw_key]
                elif normalized_key in source and normalized_key not in observations:
                    observations[normalized_key] = source[normalized_key]

    if "shadow_host" in observations or "shadow_root_mode" in observations:
        return observations

    failed_selector = ""
    failed_error_message = ""
    failed_error_stack = ""
    for record in records:
        record_type = str(record.get("type") or "").lower()
        params = record.get("params") if isinstance(record.get("params"), dict) else {}
        if record_type == "before":
            selector = str(params.get("selector") or params.get("locator") or "")
            if selector:
                failed_selector = selector
        elif record_type == "after":
            error = record.get("error") if isinstance(record.get("error"), dict) else {}
            message = str(error.get("message") or "").lower()
            stack = str(error.get("stack") or "").lower()
            if message:
                failed_error_message = message
                failed_error_stack = stack

    selector_lower = failed_selector.lower()
    has_shadow_selector = any(marker in selector_lower for marker in ("pierce", ">>", "shadow-root", "#shadow"))
    has_shadow_error = any(
        marker in failed_error_message for marker in ("cannot query field", "shadowroot", "shadow root", "closed shadow")
    )
    has_zero_elements_error = "resolved to 0 elements" in failed_error_message

    if has_shadow_error and "cannot query field" in failed_error_message:
        observations["shadow_root_mode"] = "closed"
        observations["ordinary_locator_failed"] = True
    elif has_shadow_selector and (has_zero_elements_error or failed_error_message or "shadow" in failed_error_stack):
        observations["element_exists_in_shadow_dom"] = True
        observations["ordinary_locator_failed"] = True
        parts = [part.strip() for part in failed_selector.split(">>")]
        if len(parts) >= 2:
            observations["shadow_host"] = parts[0]
            observations["inner_selector"] = parts[-1]

    return observations


def _candidate_sources(record: dict[str, Any]) -> list[dict[str, Any]]:
    sources = [record]
    params = record.get("params")
    if isinstance(params, dict):
        sources.append(params)
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        sources.append(metadata)
    return sources


def _enrich_shadow_dom_from_html(shadow_obs: dict[str, Any], html: str) -> dict[str, Any]:
    if not html:
        return shadow_obs
    html_lower = html.lower()
    has_shadow_html = "#shadow-root" in html_lower or "shadowroot" in html_lower
    if not has_shadow_html:
        return shadow_obs
    enriched = dict(shadow_obs)
    enriched.setdefault("element_exists_in_shadow_dom", True)
    custom_elements = re.findall(r"<([a-z][a-z0-9]*-[a-z0-9-]+)", html_lower)
    if custom_elements and "shadow_host" not in enriched:
        enriched["shadow_host"] = custom_elements[0]
    return enriched


def _extract_snapshot_ref(record: dict[str, Any]) -> dict[str, str] | None:
    name = record.get("snapshotName") or record.get("snapshot") or record.get("name")
    sha1 = record.get("sha1") or record.get("resourceSha1")
    record_type = str(record.get("type") or "").lower()
    if record_type != "snapshot" and not (name and sha1):
        return None
    ref: dict[str, str] = {}
    if name:
        ref["name"] = str(name)
    if sha1:
        ref["sha1"] = str(sha1)
    title = record.get("title")
    if title:
        ref["title"] = str(title)
    return ref if ref else None


def _link_snapshot_excerpts(snapshot_refs: list[dict[str, str]], text_resources: dict[str, str]) -> list[dict[str, str]]:
    excerpts: list[dict[str, str]] = []
    for ref in snapshot_refs:
        sha1 = ref.get("sha1", "")
        text = text_resources.get(sha1) or text_resources.get(sha1.lstrip("/"))
        if not text:
            continue
        excerpt = {
            "name": ref.get("name", ""),
            "sha1": sha1,
            "excerpt": text[:1000],
        }
        if excerpt not in excerpts:
            excerpts.append(excerpt)
    return excerpts


def _extract_dom_hints(html: str, missing_selectors: list[str]) -> dict[str, list[str]]:
    classes = []
    for match in re.finditer(r"\bclass\s*=\s*['\"]([^'\"]+)['\"]", html, re.IGNORECASE):
        for class_name in match.group(1).split():
            selector = f".{class_name}"
            if selector not in classes:
                classes.append(selector)

    text_candidates = []
    for text in re.findall(r">([^<>]+)<", html):
        text = re.sub(r"\s+", " ", text).strip()
        if text and text not in text_candidates:
            text_candidates.append(text)

    present_missing = [selector for selector in missing_selectors if selector and selector in html]
    missing = [selector for selector in missing_selectors if selector and selector not in present_missing]
    return {
        "missing_selectors": missing[:10],
        "candidate_selectors": [selector for selector in classes if selector not in missing][:10],
        "candidate_text": text_candidates[:10],
    }


def _is_text_resource(lower_name: str) -> bool:
    return lower_name.endswith((".html", ".dom", ".txt", ".json", ".trace", ".log"))


def _coerce_stack_text(value: Any) -> str:
    if isinstance(value, str):
        return value[:1000]
    if isinstance(value, dict):
        frames = value.get("callFrames")
        if isinstance(frames, list):
            rendered: list[str] = []
            for frame in frames[:5]:
                if not isinstance(frame, dict):
                    continue
                url = frame.get("url") or "<anonymous>"
                line = frame.get("lineNumber")
                if line is not None:
                    rendered.append(f"{url}:{line}")
                else:
                    rendered.append(str(url))
            return "\n".join(rendered)
    return ""


def _first_exception_stack(exception_details: list[dict[str, str]]) -> str:
    for detail in exception_details:
        if detail.get("stack"):
            return detail["stack"]
    return ""


def _first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return value
    return {}


def _append_unique(values: list[str], value: str, *, limit: int) -> None:
    value = value.strip()
    if not value or value in values or len(values) >= limit:
        return
    values.append(value[:500])


def _extract_status(text: str) -> int | None:
    match = re.search(r"\b(?:status|http|crawled)\D{0,12}([1-5][0-9]{2})\b", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
