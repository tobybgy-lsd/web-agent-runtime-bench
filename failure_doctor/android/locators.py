from __future__ import annotations

from typing import Any


LOCATOR_PRIORITY = [
    "resource_id",
    "accessibility_id",
    "content_desc",
    "text",
    "class_hierarchy",
    "xpath",
    "ocr_text",
    "image_match",
    "coordinate",
]


def resolve_locator(ui_tree: dict[str, Any], locator: dict[str, Any]) -> dict[str, Any]:
    nodes = ui_tree.get("nodes") or []
    warnings: list[str] = []
    if "coordinate" in locator:
        warnings.append("coordinate_locator_must_remain_fallback_only")
    if "xpath" in locator:
        warnings.append("xpath_locator_is_fragile")
    for strategy in LOCATOR_PRIORITY:
        if strategy not in locator:
            continue
        value = locator.get(strategy)
        if strategy == "accessibility_id":
            key = "content_desc"
        elif strategy == "class_hierarchy":
            key = "class_name"
        elif strategy in {"ocr_text", "image_match", "coordinate", "xpath"}:
            continue
        else:
            key = strategy
        matches = [node for node in nodes if str(node.get(key, "")) == str(value)]
        if matches:
            return {
                "status": "resolved" if len(matches) == 1 else "ambiguous",
                "strategy": strategy,
                "candidate_count": len(matches),
                "node": matches[0],
                "warnings": warnings,
            }
    return {
        "status": "not_found",
        "strategy": None,
        "candidate_count": 0,
        "node": None,
        "warnings": warnings,
    }
