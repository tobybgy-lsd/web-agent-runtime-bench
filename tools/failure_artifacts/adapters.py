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
    html_snapshot = ""
    status_code: int | None = None
    url = ""
    if not path.exists():
        raise FileNotFoundError(f"trace.zip not found: {path}")

    with ZipFile(path) as archive:
        for name in archive.namelist():
            lower = name.lower()
            data = archive.read(name)
            if "console" in lower or lower.endswith(".log"):
                console_messages.append(data.decode("utf-8", errors="replace"))
            elif lower.endswith((".html", ".dom")) or "dom" in lower:
                html_snapshot += data.decode("utf-8", errors="replace")[:5000]
            elif "network" in lower or lower.endswith(".json"):
                text = data.decode("utf-8", errors="replace")
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


def _extract_status(text: str) -> int | None:
    match = re.search(r"\b(?:status|http|crawled)\D{0,12}([1-5][0-9]{2})\b", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
