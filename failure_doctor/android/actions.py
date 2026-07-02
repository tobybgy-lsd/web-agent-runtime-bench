from __future__ import annotations

SAFE_ACTIONS = {"tap", "type", "wait", "assert_text", "select_media", "back", "switch_context"}


def is_safe_action(action: str) -> bool:
    return action in SAFE_ACTIONS
