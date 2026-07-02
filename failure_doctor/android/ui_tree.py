from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


BOUNDS_RE = re.compile(r"\[(?P<x1>-?\d+),(?P<y1>-?\d+)\]\[(?P<x2>-?\d+),(?P<y2>-?\d+)\]")


def parse_bounds(raw: str | None) -> dict[str, int] | None:
    if not raw:
        return None
    match = BOUNDS_RE.search(raw)
    if not match:
        return None
    return {key: int(value) for key, value in match.groupdict().items()}


def parse_ui_tree_xml(path: Path | str) -> dict[str, Any]:
    xml_path = Path(path)
    tree = ET.parse(xml_path)
    nodes: list[dict[str, Any]] = []
    for idx, elem in enumerate(tree.iter()):
        if elem.tag != "node":
            continue
        attrs = elem.attrib
        node = {
            "index": idx,
            "resource_id": attrs.get("resource-id") or attrs.get("resource_id") or "",
            "text": attrs.get("text") or "",
            "content_desc": attrs.get("content-desc") or attrs.get("content_desc") or "",
            "class_name": attrs.get("class") or attrs.get("className") or "",
            "package": attrs.get("package") or "",
            "bounds": parse_bounds(attrs.get("bounds")),
            "clickable": attrs.get("clickable") == "true",
            "enabled": attrs.get("enabled", "true") == "true",
            "focused": attrs.get("focused") == "true",
            "selected": attrs.get("selected") == "true",
            "raw": dict(attrs),
        }
        nodes.append(node)
    return {
        "schema_version": "android_ui_tree/v1",
        "source": str(xml_path),
        "node_count": len(nodes),
        "clickable_count": sum(1 for node in nodes if node["clickable"]),
        "nodes": nodes,
    }


def write_ui_tree_outputs(xml_path: Path | str, out_dir: Path | str) -> dict[str, Any]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    payload = parse_ui_tree_xml(xml_path)
    (output / "android_ui_tree.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
