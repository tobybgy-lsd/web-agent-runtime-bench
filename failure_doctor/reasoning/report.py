from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evidence_bundle import build_evidence_bundle
from .imported_reasoning import load as load_imported
from .llama_cpp_local import reason as llama_reason
from .mock_reasoner import reason as mock_reason
from .models import REPORT_SCHEMA
from .ollama_local import reason as ollama_reason
from .validator import validate_reasoning


def write_reasoning_report(
    input_report: Path,
    out_dir: Path,
    *,
    provider: str = "mock_reasoner",
    model: str | None = None,
    model_path: str | None = None,
    reasoning_json: Path | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_evidence_bundle(input_report)
    reasoning = _run_provider(bundle, provider, model=model, model_path=model_path, reasoning_json=reasoning_json)
    validation = validate_reasoning(bundle, reasoning)
    report = {
        "schema_version": REPORT_SCHEMA,
        "provider": provider,
        "reasoning_status": "validated" if validation["status"] == "pass" else "rejected",
        "fallback_to_rules": validation["status"] != "pass",
        "evidence_bundle": bundle,
        "claims": reasoning.get("claims", []),
        "hypotheses": reasoning.get("hypotheses", []),
        "causal_chain": reasoning.get("causal_chain", {}),
        "root_cause_graph": reasoning.get("root_cause_graph", {}),
        "competing_hypotheses": reasoning.get("competing_hypotheses", []),
        "reasoning_validation": validation,
        "external_api_call_count": reasoning.get("external_api_call_count", 0),
        "model_download_count": reasoning.get("model_download_count", 0),
    }
    _write_json(out_dir / "reasoning_evidence_bundle.json", bundle)
    _write_json(out_dir / "hybrid_reasoning_report.json", report)
    _write_json(out_dir / "causal_chain_report.json", report["causal_chain"])
    _write_json(out_dir / "root_cause_graph.json", report["root_cause_graph"])
    _write_json(out_dir / "competing_hypotheses.json", report["competing_hypotheses"])
    _write_json(out_dir / "reasoning_validation.json", validation)
    _write_json(out_dir / "reasoning_audit.json", {"provider": provider, "fallback_to_rules": report["fallback_to_rules"]})
    (out_dir / "hybrid_reasoning_summary.md").write_text(render_summary(report), encoding="utf-8")
    return report


def render_summary(report: dict[str, Any]) -> str:
    lines = ["# Hybrid Reasoning Summary", ""]
    lines.append(f"Status: `{report['reasoning_status']}`")
    lines.append(f"Provider: `{report['provider']}`")
    lines.append(f"Fallback to rules: `{report['fallback_to_rules']}`")
    lines.append("")
    lines.append("## Claims")
    if not report.get("claims"):
        lines.append("- No validated claims.")
    for claim in report.get("claims", []):
        ids = ", ".join(claim.get("supporting_evidence_ids", []))
        lines.append(f"- `{claim.get('claim_id')}` {claim.get('text')} evidence: {ids}")
    lines.append("")
    lines.append("## Hypotheses")
    for hyp in report.get("hypotheses", []):
        lines.append(f"- `{hyp.get('hypothesis_id')}` {hyp.get('title')} ({hyp.get('status')})")
    return "\n".join(lines) + "\n"


def _run_provider(
    bundle: dict[str, Any],
    provider: str,
    *,
    model: str | None,
    model_path: str | None,
    reasoning_json: Path | None,
) -> dict[str, Any]:
    if provider == "mock_reasoner":
        return mock_reason(bundle)
    if provider == "ollama_local":
        return ollama_reason(bundle, model=model)
    if provider == "llama_cpp_local":
        return llama_reason(bundle, model_path=model_path)
    if provider == "imported_reasoning" and reasoning_json:
        return load_imported(reasoning_json)
    return mock_reason(bundle)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
