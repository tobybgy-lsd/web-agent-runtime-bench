"""Evidence-node extraction for composite diagnosis.

This module keeps the inputs local and deterministic. It extracts compact,
sanitized signals from the normalized failure artifact so later stages can
reason about causal order without reading raw traces or large logs.
"""

from __future__ import annotations

import json
from typing import Any, Mapping


SECRET_MARKERS = ("authorization:", "bearer ", "cookie:", "set-cookie:", "api_key", "token=", "password=", "secret=")


def extract_evidence_nodes(artifact: Mapping[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []

    def add(
        node_type: str,
        label: str,
        *,
        source: str,
        severity: str,
        supports: list[str],
        raw_excerpt: str | None = None,
    ) -> None:
        excerpt = _sanitize_excerpt(raw_excerpt or label)
        nodes.append(
            {
                "id": f"E{len(nodes) + 1}",
                "type": node_type,
                "label": label,
                "raw_excerpt": excerpt,
                "source": source,
                "severity": severity,
                "timestamp_order": len(nodes) + 1,
                "supports": supports,
                "may_be_downstream_of": [],
            }
        )

    error = artifact.get("error") if isinstance(artifact.get("error"), Mapping) else {}
    observations = artifact.get("observations") if isinstance(artifact.get("observations"), Mapping) else {}
    error_text = " ".join([str(error.get("message") or ""), str(error.get("stack") or "")]).lower()
    user_description = str(observations.get("user_description") or "")
    strong_observations = dict(observations)
    strong_observations.pop("user_description", None)
    strong_text = f"{error_text}\n{json.dumps(strong_observations, ensure_ascii=False).lower()}"
    text = f"{strong_text}\n{user_description.lower()}"

    status = error.get("status_code") or observations.get("status_code")
    network_events = observations.get("network_events")
    if isinstance(network_events, list):
        for event in network_events[:20]:
            if not isinstance(event, Mapping):
                continue
            event_status = event.get("status")
            url = str(event.get("url") or "")
            lowered = url.lower()
            if event_status in (301, 302, 303, 307, 308) and "login" in lowered:
                add("network_event", f"{event_status} redirect to login", source="network.json", severity="high", supports=["playwright_storage_state_context", "auth_expiry"], raw_excerpt=url)
            if event_status == 401:
                add("network_event", "401 unauthorized response", source="network.json", severity="high", supports=["playwright_storage_state_context", "auth_expiry", "auth_or_permission_block"], raw_excerpt=url)
            if event_status == 403:
                add("network_event", "403 permission/access response", source="network.json", severity="high", supports=["anti_bot_risk", "network_http_error"], raw_excerpt=url)
            if event_status == 429:
                add("network_event", "429 rate limit response", source="network.json", severity="high", supports=["anti_bot_risk", "rate_limit_or_soft_block"], raw_excerpt=url)
            if event_status == 404:
                add("network_event", "404 endpoint response", source="network.json", severity="medium", supports=["network_http_error", "website_change"], raw_excerpt=url)

    if status == 429 and not any("429" in node["label"] for node in nodes):
        add("network_event", "429 rate limit response", source="error.status_code", severity="high", supports=["anti_bot_risk", "rate_limit_or_soft_block"])
    if status == 401:
        add("network_event", "401 unauthorized response", source="error.status_code", severity="high", supports=["playwright_storage_state_context", "auth_expiry"])
    if status == 403:
        add("network_event", "403 permission/access response", source="error.status_code", severity="high", supports=["anti_bot_risk", "network_http_error"])

    if any(marker in text for marker in ("redirected_to_login", "auth_redirect_detected", "/login", "login redirect")):
        add("network_event", "auth redirect/login signal", source="trace_or_log", severity="high", supports=["playwright_storage_state_context", "auth_expiry"])

    if any(marker in text for marker in ("timeout waiting for selector", "locator.click", "resolved to 0", "0 elements", "missing selector")) or (
        "timed out" in text and ("selector" in text or "locator" in text)
    ):
        add("action_failure", "selector or locator failure", source="error.log", severity="medium", supports=["selector_drift"])

    if any(marker in text for marker in ("routefromhar", "har not found", "har_loaded\": false", "route_registered_late", "live network leak")):
        add("trace_action", "route/HAR mock failure signal", source="trace_or_log", severity="high", supports=["playwright_route_mock_har"])

    if any(marker in strong_text for marker in ("proxy_connection_failed", "err_proxy", "proxy failed", "err_name_not_resolved", "dns", "err_cert", "tls", "certificate")):
        add("network_event", "network transport failure", source="error.log", severity="high", supports=["network_http_error"])

    if any(marker in strong_text for marker in ("verify you are human", "challenge page", "captcha", "too many requests", "dynamic signature", "signature invalid", "cf-ray")):
        add("console_error", "access-control or anti-abuse boundary signal", source="console_or_log", severity="high", supports=["anti_bot_risk"])

    if any(marker in text for marker in ("shadow root", "#shadow-root", "custom element", "closed shadow")):
        add("dom_signal", "shadow DOM/custom element signal", source="snapshot.html", severity="high", supports=["playwright_shadow_dom_locator"])

    if any(marker in text for marker in ("iframe", "frame detached", "frame locator")):
        add("dom_signal", "frame/iframe signal", source="trace_or_dom", severity="medium", supports=["playwright_frame_locator", "playwright_execution_context_destroyed"])

    if any(marker in text for marker in ("execution context was destroyed", "target closed", "page crashed", "cdp", "browser executable missing")):
        add("runtime_error", "runtime/page lifecycle failure", source="error.log", severity="high", supports=["playwright_execution_context_destroyed", "playwright_browser_context_closed", "cdp_websocket_disconnected", "toolchain_environment"])

    website_change_markers = (
        "jsondecodeerror",
        "cannot query field",
        "missing required fields",
        "field renamed",
        "endpoint changed",
        "response shape",
        "new component",
        "now contains",
        "now returns",
        "now uses",
        "moved into",
    )
    if any(marker in strong_text for marker in website_change_markers):
        add("console_error", "website/API shape change signal", source="log_or_network", severity="high", supports=["website_change", "response_shape_change"])

    if user_description.strip():
        add("user_description", "user-provided failure description", source="user_description", severity="medium", supports=["insufficient_evidence"], raw_excerpt=user_description)

    if not nodes:
        add("user_description", "insufficient structured evidence", source="artifact", severity="low", supports=["insufficient_evidence"])

    return nodes


def _sanitize_excerpt(text: str) -> str:
    compact = " ".join(str(text).split())
    lowered = compact.lower()
    if any(marker in lowered for marker in SECRET_MARKERS):
        compact = "[REDACTED_SECRET_LIKE_EVIDENCE]"
    if len(compact) > 220:
        compact = compact[:217] + "..."
    return compact
