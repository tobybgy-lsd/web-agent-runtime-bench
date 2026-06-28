"""Adapters that convert common tool outputs into failure artifacts.

These adapters are intentionally lightweight and local-only. They do not replay
requests or inspect real sites; they normalize already-captured evidence.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZipFile

SCHEMA_VERSION = "failure-artifact/v1"


def artifact_from_playwright_trace(trace_zip: Path | str, *, run_id: str | None = None) -> dict[str, Any]:
    path = Path(trace_zip)
    console_messages: list[str] = []
    network_events: list[dict[str, Any]] = []
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
            status_code = _extract_status(text) or status_code
            for record in _parse_json_records(text):
                for message in _extract_record_messages(record):
                    _append_unique(console_messages, message, limit=20)
                event = _extract_network_event(record)
                if event:
                    if event not in network_events:
                        network_events.append(event)
                    status_code = _as_int(event.get("status")) or status_code
                    url = str(event.get("url") or url)

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

    return _base_artifact(
        run_id=run_id,
        tool="playwright",
        summary="Collected from Playwright trace.zip",
        status_code=status_code,
        error_message=" ".join(console_messages)[:500],
        artifacts={"trace": path.name, "html_snapshot": "snapshot.html"} if html_snapshot else {"trace": path.name},
        observations={
            "source_adapter": "playwright_trace",
            "url": url,
            "console_messages": console_messages,
            "network_events": network_events[:20],
            "html_excerpt": html_snapshot[:1000],
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
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or f"{tool}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "tool": tool,
        "target_type": "sanitized_real_failure",
        "summary": summary,
        "error": {"message": error_message, "stack": "", "status_code": status_code},
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
    return event if event else None


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
