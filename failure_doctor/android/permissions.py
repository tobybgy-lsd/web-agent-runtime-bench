from __future__ import annotations


def permission_next_action(permission: str) -> str:
    return f"Verify {permission} is required for the owned test app, then grant it in the authorized test profile."
