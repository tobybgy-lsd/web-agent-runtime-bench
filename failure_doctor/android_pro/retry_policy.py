from __future__ import annotations


def default_retry_policy() -> dict:
    return {"max_attempts": 2, "requires_checkpoint": True, "manual_review_after_exhausted": True}
