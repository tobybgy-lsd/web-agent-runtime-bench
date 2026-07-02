from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def write_md(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", "", *lines, ""]
    path.write_text("\n".join(body), encoding="utf-8")


def base_payload(schema: str, version: str, status: str = "pass") -> dict[str, Any]:
    return {
        "schema_version": schema,
        "tool_version": version,
        "status": status,
        "created_at": now_iso(),
        "local_only": True,
        "no_upload": True,
        "no_telemetry": True,
        "sanitized_by_default": True,
        "dry_run_default": True,
        "allow_final_submit": False,
        "allow_business_mutation": False,
        "external_api_call_count": 0,
        "screenshot_upload_count": 0,
        "apk_modification_count": 0,
        "hook_usage_count": 0,
        "root_required_count": 0,
        "real_business_mutation_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "real_platform_access_count": 0,
    }


def safe_report(kind: str, version: str, out: Path, **extra: Any) -> dict[str, Any]:
    payload = base_payload(f"{kind}/v1", version)
    payload.update(extra)
    write_json(out / f"{kind}.json", payload)
    write_md(out / f"{kind}.md", kind.replace("_", " ").title(), [
        f"- Status: `{payload['status']}`",
        "- Mode: local-only sanitized dry-run.",
        "- Final submit and business mutation are blocked by default.",
    ])
    return payload
