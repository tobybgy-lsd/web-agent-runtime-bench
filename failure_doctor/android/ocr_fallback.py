from __future__ import annotations


def ocr_fallback_decision(confidence: float) -> dict[str, object]:
    return {"status": "usable" if confidence >= 0.8 else "low_confidence", "confidence": confidence, "external_upload": False}
