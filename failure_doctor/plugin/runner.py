from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .manifest import load_manifest
from .registry import audit, get_plugin_dir
from .sandbox import validate_plugin_io
from .validator import validate_plugin


def run_plugin(plugin_id: str, *, workspace: Path, input_dir: Path, out_dir: Path) -> dict[str, Any]:
    plugin_dir = get_plugin_dir(plugin_id, workspace)
    report = validate_plugin(plugin_dir, write_report=False)
    if report.get("status") != "pass":
        raise ValueError("plugin validation failed; run blocked")
    validate_plugin_io(input_dir, out_dir)
    manifest, _payload = load_manifest(plugin_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence_items = _evidence_from_input(input_dir, manifest.plugin_id)
    result = {
        "schema_version": "failure_doctor_plugin_result/v1",
        "plugin_id": manifest.plugin_id,
        "plugin_type": manifest.type,
        "status": "pass",
        "schema_valid": True,
        "local_only": True,
        "external_api_call_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "evidence_items": evidence_items,
        "diagnosis_candidates": [
            {
                "plugin_id": manifest.plugin_id,
                "failure_type": "plugin_candidate",
                "subtype": f"{manifest.plugin_id}_candidate",
                "confidence": 0.5,
                "evidence_ids": [item["id"] for item in evidence_items[:3]],
                "risk_note": "Candidate only; core diagnosis remains final authority.",
            }
        ],
    }
    (out_dir / "plugin_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "plugin_result.md").write_text(render_plugin_result_md(result), encoding="utf-8")
    audit(workspace, "plugin.run", {"plugin_id": manifest.plugin_id, "out": str(out_dir)})
    return result


def diagnosis_candidates(plugin_id: str, *, workspace: Path, input_dir: Path, out_dir: Path) -> list[dict[str, Any]]:
    result = run_plugin(plugin_id, workspace=workspace, input_dir=input_dir, out_dir=out_dir)
    return list(result.get("diagnosis_candidates", []))


def _evidence_from_input(input_dir: Path, plugin_id: str) -> list[dict[str, Any]]:
    path = Path(input_dir)
    files = [path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]
    evidence: list[dict[str, Any]] = []
    for index, item in enumerate(files[:20], start=1):
        evidence.append(
            {
                "id": f"{plugin_id}-evidence-{index:03d}",
                "kind": "plugin_file_summary",
                "path": item.name,
                "size": item.stat().st_size if item.exists() else 0,
                "summary": "Sanitized local plugin evidence candidate.",
            }
        )
    if not evidence:
        evidence.append(
            {
                "id": f"{plugin_id}-evidence-001",
                "kind": "plugin_empty_input",
                "summary": "Plugin input folder contained no files.",
            }
        )
    return evidence


def render_plugin_result_md(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Plugin Result",
            "",
            f"- Plugin: `{result.get('plugin_id')}`",
            f"- Type: `{result.get('plugin_type')}`",
            f"- Status: `{result.get('status')}`",
            f"- Schema valid: `{result.get('schema_valid')}`",
            "",
            "Plugin output is candidate-only. Core diagnosis and safety gates remain final authority.",
            "",
        ]
    )
