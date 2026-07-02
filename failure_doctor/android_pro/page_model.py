from __future__ import annotations

from pathlib import Path
from typing import Any

from . import ANDROID_PRO_VERSION
from .common import locator_for_node, node_role, parse_ui_nodes, write_json


def build_page_model(ui_dump: Path, out: Path, page_id: str = "detected_page") -> dict[str, Any]:
    nodes = parse_ui_nodes(ui_dump)
    elements = []
    for node in nodes:
        role = node_role(node)
        locator = locator_for_node(node)
        stability = "high" if locator["strategy"] in {"resource_id", "accessibility_id"} else "medium" if locator["strategy"] == "text" else "low"
        elements.append(
            {
                "element_id": _element_id(role, len(elements)),
                "role": role,
                "resource_id": node.get("resource_id", ""),
                "text": node.get("text", ""),
                "content_desc": node.get("content_desc", ""),
                "class_name": node.get("class_name", ""),
                "bounds": node.get("bounds", ""),
                "stability": stability,
                "recommended_locator": locator,
            }
        )
    payload = {
        "schema_version": "android_page_model/v1",
        "tool_version": ANDROID_PRO_VERSION,
        "page_id": page_id,
        "detected_from": str(ui_dump),
        "elements": elements,
    }
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / f"{page_id}.json", payload)
    return payload


def _element_id(role: str, index: int) -> str:
    return f"{role}_{index + 1}"
