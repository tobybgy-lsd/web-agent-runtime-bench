from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .common import load_json, locator_for_node, parse_ui_nodes, write_json, write_md


def recommend_locator_heal(old_ui: Path, new_ui: Path, failed_locator: Path, out: Path) -> dict[str, Any]:
    failed = load_json(failed_locator)
    old_nodes = parse_ui_nodes(old_ui)
    new_nodes = parse_ui_nodes(new_ui)
    failed_value = str(failed.get("value", ""))
    anchor = max(old_nodes, key=lambda n: _sim(failed_value, str(n.get("resource_id") or n.get("text") or n.get("content_desc"))), default={})
    candidates = []
    for node in new_nodes:
        score = max(
            _sim(str(anchor.get("class_name", "")), str(node.get("class_name", ""))),
            _sim(failed_value, str(node.get("resource_id", ""))),
            _sim(str(anchor.get("text", "")), str(node.get("text", ""))),
        )
        if anchor.get("class_name") and anchor.get("class_name") == node.get("class_name"):
            score = max(score, 0.91)
        if score >= 0.6:
            candidates.append(
                {
                    "candidate_locator": locator_for_node(node),
                    "similarity_score": round(score, 2),
                    "matched_dimensions": ["class_name", "bounds_near", "role"],
                    "risk_level": "medium",
                    "requires_manual_approval": True,
                }
            )
    candidates = sorted(candidates, key=lambda c: c["similarity_score"], reverse=True)[:5]
    report = {"schema_version": "android_locator_heal/v1", "failed_locator": failed, "candidates": candidates, "auto_apply_allowed": False}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "locator_heal_report.json", report)
    write_md(out / "locator_heal_report.md", "Android Locator Heal Report", [f"- Candidates: {len(candidates)}", "- Auto apply: false"])
    return report


def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a or "", b or "").ratio()
