from __future__ import annotations


def image_fallback_decision(confidence: float) -> dict[str, object]:
    return {"status": "usable" if confidence >= 0.85 else "low_confidence", "confidence": confidence, "external_upload": False}
