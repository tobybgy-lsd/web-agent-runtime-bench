from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import parse_ui_nodes, write_json, write_md


def diff_ui_trees(old: Path, new: Path, out: Path) -> dict[str, Any]:
    old_nodes = parse_ui_nodes(old)
    new_nodes = parse_ui_nodes(new)
    changes: list[dict[str, Any]] = []
    max_len = max(len(old_nodes), len(new_nodes))
    for idx in range(max_len):
        if idx >= len(old_nodes):
            changes.append({"type": "node_added", "index": idx, "new": new_nodes[idx]})
            continue
        if idx >= len(new_nodes):
            changes.append({"type": "node_removed", "index": idx, "old": old_nodes[idx]})
            continue
        old_node, new_node = old_nodes[idx], new_nodes[idx]
        for field in ("resource_id", "text", "content_desc", "class_name", "bounds"):
            if old_node.get(field) != new_node.get(field):
                changes.append({"type": f"{field}_changed", "index": idx, "old": old_node.get(field), "new": new_node.get(field)})
    report = {"schema_version": "android_ui_tree_diff/v1", "status": "pass", "old_node_count": len(old_nodes), "new_node_count": len(new_nodes), "changes": changes}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "ui_tree_diff_report.json", report)
    write_md(out / "ui_tree_diff_report.md", "Android UI Tree Diff", [f"- Changes: {len(changes)}"])
    return report
