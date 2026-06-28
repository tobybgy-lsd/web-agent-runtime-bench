from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from zipfile import ZIP_DEFLATED, ZipFile

from tools.failure_artifacts.adapters import artifact_from_playwright_trace
from tools.failure_artifacts.diagnose import diagnose_artifact
from tools.failure_artifacts.issue import render_issue_draft
from tools.failure_artifacts.reporter import render_markdown_report
from trace_doctor.cli import _render_repair_suggestions


NEXT_ACTION = "把 codex_fix_prompt.md 交给 Codex/Claude 修改代码"


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diagnose":
        return diagnose_inputs(args)
    parser.print_help()
    return 1


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="failure_doctor",
        description="Agent Failure Doctor: diagnose local AI automation failures from traces, logs, network captures, and descriptions.",
    )
    sub = parser.add_subparsers(dest="command")
    diagnose = sub.add_parser("diagnose", help="Diagnose a local failure input file or directory")
    diagnose.add_argument("input", help="Path to trace.zip, log file, network.json, description file, screenshot, or a directory")
    diagnose.add_argument("--out", required=True, help="Output report directory")
    diagnose.add_argument("--run-id", default=None, help="Stable run identifier")
    return parser


def diagnose_inputs(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    out_dir = Path(args.out)
    if not input_path.exists():
        print(f"input not found: {input_path}")
        return 1

    evidence = collect_inputs(input_path)
    artifact = build_artifact(evidence, run_id=args.run_id)
    diagnosis = diagnose_artifact(artifact)
    public = enrich_for_users(diagnosis)
    outputs = write_failure_doctor_report(out_dir, artifact, diagnosis, public, evidence)

    confidence = float(public.get("confidence", 0.0))
    print("Agent Failure Doctor")
    print(f"Category: {public.get('user_facing_category')} ({confidence:.0%})")
    print(f"Technical: {public.get('technical_category')} / {public.get('subtype', 'n/a')}")
    print(f"Next: {public.get('next_action')}")
    print(f"Report: {out_dir}")
    print(f"Bundle: {outputs['failure_doctor_report.zip']}")
    return 0


def collect_inputs(path: Path) -> dict[str, Any]:
    files = [path] if path.is_file() else sorted(item for item in path.iterdir() if item.is_file())
    evidence: dict[str, Any] = {
        "source": str(path),
        "trace_zip": None,
        "logs": [],
        "network_events": [],
        "descriptions": [],
        "screenshot_metadata": [],
        "unrecognized_files": [],
    }
    for file_path in files:
        lower = file_path.name.lower()
        if lower.endswith(".zip") and "trace" in lower:
            evidence["trace_zip"] = str(file_path)
        elif lower.endswith((".log", ".txt")) and ("description" not in lower and "readme" not in lower):
            evidence["logs"].append({"name": file_path.name, "text": _read_text(file_path)})
        elif lower.endswith(".json") and "network" in lower:
            evidence["network_events"].extend(_read_network_events(file_path))
        elif lower.endswith(".txt") and ("description" in lower or "user" in lower):
            evidence["descriptions"].append({"name": file_path.name, "text": _read_text(file_path)})
        elif lower.endswith((".png", ".jpg", ".jpeg")):
            evidence["screenshot_metadata"].append(
                {"name": file_path.name, "size_bytes": file_path.stat().st_size, "image_understanding": "metadata_only"}
            )
        else:
            evidence["unrecognized_files"].append(file_path.name)
    return evidence


def build_artifact(evidence: Mapping[str, Any], *, run_id: str | None = None) -> dict[str, Any]:
    trace_zip = evidence.get("trace_zip")
    if trace_zip:
        artifact = artifact_from_playwright_trace(Path(str(trace_zip)), run_id=run_id)
        observations = artifact.setdefault("observations", {})
        if isinstance(observations, dict):
            observations["failure_doctor_inputs"] = _input_summary(evidence)
        return artifact

    log_text = "\n".join(str(item.get("text", "")) for item in evidence.get("logs", []) if isinstance(item, Mapping))
    description_text = "\n".join(str(item.get("text", "")) for item in evidence.get("descriptions", []) if isinstance(item, Mapping))
    network_events = evidence.get("network_events", [])
    status_code = _first_status(network_events) or _extract_status_from_text(log_text)
    diagnosis_hint = _diagnosis_hint_from_text(log_text, description_text, network_events)
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": run_id or f"failure_doctor_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "tool": "agent_failure_doctor",
        "target_type": "sanitized_real_failure",
        "summary": "Collected from local AI automation failure inputs",
        "error": {"message": (log_text or description_text)[:500], "stack": "", "status_code": status_code},
        "artifacts": {},
        "observations": {
            "source_adapter": "failure_doctor",
            "log_excerpt": log_text[:1000],
            "user_description": description_text[:1000],
            "network_events": network_events[:20],
            "missing_selectors": diagnosis_hint.get("missing_selectors", []),
            "screenshot_metadata": evidence.get("screenshot_metadata", []),
            **diagnosis_hint,
        },
        "expected": {"required_fields": diagnosis_hint.get("expected_fields", [])},
        "actual": {"fields": diagnosis_hint.get("actual_fields", {}), "array_length": diagnosis_hint.get("array_length")},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
            "redaction_notes": "Generated from local user-provided failure inputs; review before sharing.",
        },
    }


def enrich_for_users(diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    technical = str(diagnosis.get("failure_type", "unknown"))
    subtype = str(diagnosis.get("subtype", ""))
    category = user_category_for(technical, subtype)
    return {
        "user_facing_category": category,
        "technical_category": technical,
        "subtype": diagnosis.get("subtype"),
        "confidence": diagnosis.get("confidence", 0.0),
        "evidence_level": diagnosis.get("evidence_level", "inferred"),
        "evidence": diagnosis.get("evidence", []),
        "suggested_fix": diagnosis.get("suggested_fix", []),
        "next_action": NEXT_ACTION,
    }


def user_category_for(technical: str, subtype: str = "") -> str:
    if technical in {"auth_expiry", "playwright_storage_state_context"}:
        return "登录状态失效"
    if technical in {"selector_drift", "playwright_shadow_dom_locator", "playwright_strict_mode_violation", "playwright_frame_locator"}:
        return "按钮/元素找不到"
    if technical in {"async_hydration_timing", "playwright_execution_context_destroyed"}:
        return "页面没加载完"
    if technical in {"playwright_popup"}:
        return "弹窗/遮罩挡住"
    if technical == "response_shape_change" or (technical == "playwright_route_mock_har" and subtype == "mock_response_shape_mismatch"):
        return "接口返回变了"
    if technical == "rate_limit_or_soft_block":
        return "请求被限流"
    if technical == "network_http_error":
        return "网络/代理问题"
    if technical in {"runtime_api_missing", "toolchain_environment", "playwright_browser_context_closed", "cdp_websocket_disconnected"}:
        return "浏览器环境不一致"
    if technical in {"playwright_file_chooser", "playwright_download"}:
        return "文件上传下载失败"
    return "代码等待逻辑错误"


def write_failure_doctor_report(
    out_dir: Path,
    artifact: Mapping[str, Any],
    diagnosis: Mapping[str, Any],
    public: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "diagnosis.json": out_dir / "diagnosis.json",
        "diagnosis.md": out_dir / "diagnosis.md",
        "evidence.json": out_dir / "evidence.json",
        "repair_suggestions.md": out_dir / "repair_suggestions.md",
        "issue_draft.md": out_dir / "issue_draft.md",
        "codex_fix_prompt.md": out_dir / "codex_fix_prompt.md",
        "failure_doctor_report.zip": out_dir / "failure_doctor_report.zip",
    }
    diagnosis_payload = {**dict(public), "raw_diagnosis": dict(diagnosis)}
    outputs["diagnosis.json"].write_text(_json(diagnosis_payload), encoding="utf-8")
    outputs["diagnosis.md"].write_text(_render_public_markdown(public, diagnosis, artifact), encoding="utf-8")
    outputs["evidence.json"].write_text(_json({"inputs": evidence, "artifact": artifact, "diagnosis": diagnosis_payload}), encoding="utf-8")
    outputs["repair_suggestions.md"].write_text(_render_repair_suggestions(diagnosis), encoding="utf-8")
    outputs["issue_draft.md"].write_text(render_issue_draft(artifact, diagnosis, _doctor_summary(diagnosis)), encoding="utf-8")
    outputs["codex_fix_prompt.md"].write_text(_render_codex_fix_prompt(public, diagnosis), encoding="utf-8")
    _write_report_zip(out_dir, outputs["failure_doctor_report.zip"])
    return outputs


def _diagnosis_hint_from_text(log_text: str, description_text: str, network_events: Any) -> dict[str, Any]:
    text = f"{log_text}\n{description_text}".lower()
    hints: dict[str, Any] = {}
    if "err_proxy_connection_failed" in text or "proxy_connection_failed" in text:
        hints.update({"network_error": "proxy connection failed", "transport_marker": "proxy", "subtype_hint": "proxy_connection_failed"})
    if "err_name_not_resolved" in text:
        hints.update({"network_error": "dns name not resolved", "transport_marker": "dns", "subtype_hint": "dns_name_not_resolved"})
    if "err_cert_authority_invalid" in text or "err_cert" in text or "certificate" in text:
        hints.update({"network_error": "tls certificate error", "transport_marker": "tls", "subtype_hint": "tls_certificate_error"})
    if "strict mode violation" in text:
        hints["strict_mode_violation"] = True
    if "timeout waiting for selector" in text or "locator.click" in text:
        hints["missing_selectors"] = ["button.submit" if "button.submit" in text else "unknown"]
    if "page.goto" in text and "timeout" in text:
        hints["navigation_timeout"] = True
    if "page stayed" in text or "never worked" in text:
        hints["wait_or_click_failed"] = True
    statuses = [item.get("status") for item in network_events if isinstance(item, Mapping)]
    if 429 in statuses or "429" in text:
        hints["rate_limit_marker"] = True
    return hints


def _read_network_events(path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


def _first_status(events: Any) -> int | None:
    if not isinstance(events, list):
        return None
    for event in events:
        if isinstance(event, Mapping):
            status = event.get("status") or event.get("status_code")
            try:
                return int(status)
            except (TypeError, ValueError):
                continue
    return None


def _extract_status_from_text(text: str) -> int | None:
    for status in (401, 403, 429, 500, 502, 503):
        if str(status) in text:
            return status
    return None


def _render_public_markdown(public: Mapping[str, Any], diagnosis: Mapping[str, Any], artifact: Mapping[str, Any]) -> str:
    evidence = "\n".join(f"- {item}" for item in public.get("evidence", [])) or "- No evidence generated."
    return "\n".join(
        [
            "# Agent Failure Diagnosis",
            "",
            f"- User-facing category: `{public.get('user_facing_category')}`",
            f"- Technical category: `{public.get('technical_category')}`",
            f"- Subtype: `{public.get('subtype', 'n/a')}`",
            f"- Confidence: `{public.get('confidence', 0)}`",
            f"- Next action: {public.get('next_action')}",
            "",
            "## Plain-English Summary",
            "",
            _plain_summary(public),
            "",
            "## Evidence",
            "",
            evidence,
            "",
            "## Technical Details",
            "",
            render_markdown_report(diagnosis, artifact),
        ]
    )


def _plain_summary(public: Mapping[str, Any]) -> str:
    category = public.get("user_facing_category")
    technical = public.get("technical_category")
    return f"这个失败更像是“{category}”，不是单纯的代码语法错误。技术分类是 `{technical}`。"


def _render_codex_fix_prompt(public: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> str:
    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", [])) or "- 证据不足，需要先补充日志或 trace。"
    fixes = "\n".join(f"- {item}" for item in diagnosis.get("suggested_fix", [])) or "- 根据诊断结果做最小修复。"
    return f"""# Codex Fix Prompt

请修复这个 AI 自动化失败。

## 诊断结果

- 大类：{public.get("user_facing_category")}
- 技术原因：{public.get("technical_category")}
- 子类型：{public.get("subtype", "n/a")}
- 置信度：{public.get("confidence", 0)}

## 证据

{evidence}

## 修改要求

{fixes}

## 约束

1. 不要改业务逻辑。
2. 不要加入 Cookie、Token、Authorization 或密码。
3. 不要加入 CAPTCHA 绕过或反爬规避逻辑。
4. 添加失败时 trace/screenshot/log 保存。
5. 修改后运行相关测试或 smoke test。
"""


def _doctor_summary(diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ready": True,
        "checks": [{"name": "failure_doctor", "status": "pass", "detail": "local multi-input diagnosis generated"}],
        "errors": [],
        "next_steps": ["review codex_fix_prompt.md before giving it to a coding assistant"],
        "diagnosis": dict(diagnosis),
    }


def _input_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "trace_zip": evidence.get("trace_zip"),
        "log_count": len(evidence.get("logs", [])),
        "network_event_count": len(evidence.get("network_events", [])),
        "description_count": len(evidence.get("descriptions", [])),
        "screenshot_count": len(evidence.get("screenshot_metadata", [])),
    }


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")[:5000]


def _write_report_zip(root: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.iterdir()):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.name)


def _json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
