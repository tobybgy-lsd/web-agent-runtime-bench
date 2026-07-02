from __future__ import annotations


def coordinate_fallback_policy() -> dict[str, object]:
    return {"allowed": True, "fallback_only": True, "requires_ui_tree_evidence": True}
