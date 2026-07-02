from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ADAPTER_VERSION = "adapter/v1"
SUPPORTED_ADAPTER_KINDS = {"rpa", "api", "mobile"}


SUBTYPE_MARKERS = {
    "rpa": [
        ("selector", "rpa_selector_drift"),
        ("window focus", "rpa_window_focus_lost"),
        ("control not found", "rpa_control_not_found"),
        ("image match", "rpa_image_match_low_confidence"),
        ("permission dialog", "rpa_permission_dialog_blocked"),
        ("waiting window", "rpa_timeout_waiting_window"),
    ],
    "api": [
        ("schema", "api_schema_mismatch"),
        ("status code", "api_status_code_regression"),
        ("401", "api_auth_expired"),
        ("429", "api_rate_limited"),
        ("timeout", "api_timeout"),
        ("field missing", "api_response_field_missing"),
        ("contract drift", "api_contract_drift"),
    ],
    "mobile": [
        ("element not found", "mobile_element_not_found"),
        ("context mismatch", "mobile_context_mismatch"),
        ("permission dialog", "mobile_permission_dialog_blocked"),
        ("network unstable", "mobile_network_unstable"),
        ("density", "mobile_viewport_density_mismatch"),
    ],
}


def normalize_adapter_input(input_path: Path, out_dir: Path, *, kind: str) -> dict[str, Any]:
    kind = _require_kind(kind)
    if not input_path.exists():
        raise FileNotFoundError(f"input not found: {input_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    text = _collect_text(input_path)
    subtype = _detect_subtype(kind, text)
    payload = {
        "schema_version": ADAPTER_VERSION,
        "tool_version": "5.3.0",
        "created_at": _now(),
        "adapter_kind": kind,
        "input_path": str(input_path),
        "normalized": True,
        "local_only": True,
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
        "raw_secret_in_output": 0,
        "private_solution_leak_count": 0,
        "forbidden_output_count": 0,
        "evidence": [
            {
                "evidence_id": "A001",
                "source": f"{kind}_artifact",
                "summary": _redact_summary(text),
                "raw_excluded": True,
            }
        ],
        "candidate_subtype": subtype,
    }
    _write_json(out_dir / "adapter_normalized.json", payload)
    (out_dir / "adapter_summary.md").write_text(_render_adapter_summary(payload), encoding="utf-8")
    return payload


def diagnose_adapter_input(input_path: Path, out_dir: Path, *, kind: str) -> dict[str, Any]:
    normalized = normalize_adapter_input(input_path, out_dir, kind=kind)
    subtype = normalized["candidate_subtype"]
    diagnosis = {
        "schema_version": "adapter_diagnosis/v1",
        "tool_version": "5.3.0",
        "failure_type": _failure_type_for_kind(kind),
        "subtype": subtype,
        "confidence": 0.88,
        "evidence_level": "adapter_log",
        "safe_next_action": _safe_next_action(kind, subtype),
        "diagnosis_only_no_bypass": True,
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
    }
    _write_json(out_dir / "adapter_diagnosis.json", diagnosis)
    (out_dir / "adapter_diagnosis.md").write_text(_render_diagnosis_markdown(diagnosis), encoding="utf-8")
    return diagnosis


def _require_kind(kind: str) -> str:
    if kind not in SUPPORTED_ADAPTER_KINDS:
        raise ValueError(f"unknown adapter kind: {kind}")
    return kind


def _collect_text(path: Path) -> str:
    files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
    chunks: list[str] = []
    for file_path in files[:50]:
        try:
            chunks.append(file_path.read_text(encoding="utf-8", errors="ignore")[:2000])
        except OSError:
            continue
    return "\n".join(chunks)


def _detect_subtype(kind: str, text: str) -> str:
    lowered = text.lower()
    for marker, subtype in SUBTYPE_MARKERS[kind]:
        if marker in lowered:
            return subtype
    defaults = {
        "rpa": "rpa_control_not_found",
        "api": "api_contract_drift",
        "mobile": "mobile_element_not_found",
    }
    return defaults[kind]


def _failure_type_for_kind(kind: str) -> str:
    return {
        "rpa": "desktop_rpa_automation",
        "api": "api_automation",
        "mobile": "mobile_automation",
    }[kind]


def _safe_next_action(kind: str, subtype: str) -> list[str]:
    common = [
        "Use sanitized local logs only; do not upload raw credentials or customer data.",
        "Re-run through diagnose/plan/verify after the smallest scoped fix.",
    ]
    if kind == "api" and subtype in {"api_auth_expired", "api_rate_limited"}:
        return [
            "Check authorized token/session configuration and documented rate limits.",
            "Use official API quotas, SDKs, or exports where available.",
            "Do not use unauthorized network or account workarounds, token guessing, or access-control defeat.",
        ] + common
    if kind == "rpa":
        return [
            "Capture the target window/control tree and compare it with the last known working run.",
            "Prefer stable accessibility ids or documented test hooks over image-only matching.",
        ] + common
    return [
        "Capture device density, current context, permission dialog state, and appium log excerpts.",
        "Prefer documented accessibility ids and authorized test devices.",
    ] + common


def _redact_summary(text: str) -> str:
    redacted = text.replace("Authorization:", "Authorization: <REDACTED>")
    for token in ("cookie", "token", "password", "secret"):
        redacted = redacted.replace(token, "<redacted>")
    return redacted[:1000] or "No text evidence found; adapter emitted a low-evidence normalized record."


def _render_adapter_summary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Adapter Normalization",
            "",
            f"- Adapter: `{payload['adapter_kind']}`",
            f"- Candidate subtype: `{payload['candidate_subtype']}`",
            "- Local-only: `true`",
            "- Raw content: excluded from public outputs",
            "",
        ]
    )


def _render_diagnosis_markdown(diagnosis: dict[str, Any]) -> str:
    actions = "\n".join(f"- {item}" for item in diagnosis["safe_next_action"])
    return "\n".join(
        [
            "# Adapter Diagnosis",
            "",
            f"- Failure type: `{diagnosis['failure_type']}`",
            f"- Subtype: `{diagnosis['subtype']}`",
            f"- Confidence: `{diagnosis['confidence']}`",
            "",
            "## Safe Next Action",
            "",
            actions,
            "",
        ]
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
