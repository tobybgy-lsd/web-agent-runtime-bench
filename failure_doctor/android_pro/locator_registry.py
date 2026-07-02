from __future__ import annotations

from pathlib import Path
from typing import Any

from . import ANDROID_PRO_VERSION
from .common import load_json, locator_for_node, node_role, parse_ui_nodes, write_json, write_md


def build_locator_registry(ui_dump: Path, out: Path, profile_id: str = "android_profile") -> dict[str, Any]:
    pages: dict[str, Any] = {"detected_page": {}}
    for node in parse_ui_nodes(ui_dump):
        locator = locator_for_node(node)
        role = node_role(node)
        element_id = f"{role}_{len(pages['detected_page']) + 1}"
        risk = "low" if locator["strategy"] in {"resource_id", "accessibility_id"} else "medium" if locator["strategy"] == "text" else "high"
        pages["detected_page"][element_id] = {
            "primary": locator,
            "fallbacks": [{"strategy": "class_hierarchy", "value": f"{node.get('class_name')}[{node.get('index', 0)}]"}],
            "risk_level": risk,
        }
    payload = {"schema_version": "android_locator_registry/v1", "tool_version": ANDROID_PRO_VERSION, "profile_id": profile_id, "pages": pages}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_locator_registry.json", payload)
    write_md(out / "locator_registry_summary.md", "Android Locator Registry", [f"- Pages: {len(pages)}"])
    payload["status"] = "pass"
    return payload


def validate_locator_registry(registry: Path) -> dict[str, Any]:
    path = registry / "android_locator_registry.json" if registry.is_dir() else registry
    payload = load_json(path)
    findings: list[dict[str, Any]] = []
    for page_id, elements in payload.get("pages", {}).items():
        for element_id, entry in elements.items():
            primary = entry.get("primary", {})
            if primary.get("strategy") == "coordinate":
                findings.append({"severity": "critical", "code": "absolute_coordinate_primary_blocked", "page_id": page_id, "element_id": element_id})
            if primary.get("strategy") == "xpath":
                findings.append({"severity": "warning", "code": "xpath_primary_fragile", "page_id": page_id, "element_id": element_id})
    report = {"schema_version": "android_locator_registry_validation/v1", "status": "pass" if not any(f["severity"] == "critical" for f in findings) else "fail", "findings": findings}
    write_json(path.parent / "locator_registry_validation.json", report)
    return report
