from __future__ import annotations

from typing import Any


def diagnose_ocr_evidence(
    ocr: dict[str, Any],
    *,
    dom_report: dict[str, Any] | None = None,
    vlm_report: dict[str, Any] | None = None,
    quality_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    subtype = "ocr_insufficient_evidence"
    confidence = 0.55
    evidence: list[str] = []
    warnings = set(ocr.get("warnings", []))
    safety = ocr.get("safety", {})
    if safety.get("shareability_decision") == "blocked":
        subtype = "ocr_cloud_upload_blocked" if "ocr_cloud_upload_blocked" in warnings else "ocr_sensitive_data_detected"
        confidence = 0.94
        evidence.append("OCR safety policy blocked sharing or cloud provider use.")
    elif safety.get("shareability_decision") == "sanitize_required":
        subtype = "ocr_sensitive_data_detected"
        confidence = 0.92
        evidence.append("OCR evidence contains sensitive-looking text and requires sanitization.")
    elif "provider_unavailable" in warnings:
        subtype = "ocr_provider_unavailable"
        confidence = 0.86
        evidence.append("Requested OCR provider is unavailable; no external fallback was used.")
    elif "compression_loss" in warnings:
        subtype = "ocr_screenshot_compression_loss"
        confidence = 0.86
        evidence.append("OCR fixture marks screenshot text as degraded by compression.")
    elif "rotation_or_skew" in warnings:
        subtype = "ocr_rotation_or_skew_issue"
        confidence = 0.84
        evidence.append("OCR fixture marks rotation or skew as lowering text reliability.")
    elif "low_contrast" in warnings:
        subtype = "ocr_low_contrast_unreadable"
        confidence = 0.84
        evidence.append("OCR fixture marks low-contrast text as weak evidence.")
    elif "multilingual_confidence_drop" in warnings:
        subtype = "ocr_multilingual_confidence_drop"
        confidence = 0.82
        evidence.append("OCR confidence drops for multilingual text.")
    elif dom_report and dom_report.get("findings"):
        subtype = "ocr_dom_text_conflict"
        confidence = 0.9
        evidence.append("OCR text conflicts with DOM text.")
    elif vlm_report and vlm_report.get("findings"):
        subtype = "ocr_vlm_semantic_conflict"
        confidence = 0.9
        evidence.append("OCR text conflicts with offline VLM response.")
    elif quality_report and quality_report.get("findings"):
        first = quality_report["findings"][0]["type"]
        subtype = {
            "ocr_table_column_shift": "ocr_table_column_shift",
            "price_field_not_numeric": "ocr_form_label_value_mismatch",
            "required_form_field_missing": "ocr_form_label_value_mismatch",
            "sku_column_missing": "ocr_table_column_shift",
            "duplicate_table_rows": "ocr_table_row_merge_error",
        }.get(first, "ocr_low_confidence")
        confidence = 0.87
        evidence.append(f"OCR data-quality finding detected: {first}.")
    elif not ocr.get("text_blocks") and not ocr.get("tables") and not ocr.get("forms"):
        subtype = "ocr_text_missing"
        confidence = 0.78
        evidence.append("No OCR text, tables, or forms were extracted.")
    elif ocr.get("confidence_summary", {}).get("overall", 0) < 0.65:
        subtype = "ocr_low_confidence"
        confidence = 0.8
        evidence.append("Overall OCR confidence is low.")
    else:
        subtype = "ocr_evidence_available"
        confidence = 0.82
        evidence.append("OCR evidence was extracted and can be compared locally.")
    return {
        "failure_type": "ocr_document_evidence",
        "subtype": subtype,
        "evidence": evidence,
        "confidence": confidence,
        "risk_level": "medium" if subtype != "ocr_evidence_available" else "low",
        "safe_next_action": "Compare OCR evidence with DOM, VLM responses, exported schema, or data-quality checks locally.",
        "verification_strategy": "Re-run OCR extraction after improving screenshot/document capture and compare reports.",
    }
