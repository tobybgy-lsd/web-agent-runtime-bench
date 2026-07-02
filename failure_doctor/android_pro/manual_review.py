from __future__ import annotations


def manual_review_required(reason: str) -> dict:
    return {"required": True, "reason": reason}
