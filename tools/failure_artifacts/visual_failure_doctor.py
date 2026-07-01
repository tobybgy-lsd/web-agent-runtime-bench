"""Visual failure diagnostics for screenshot, DOM, OCR, and click evidence.

The module is intentionally local-first and evidence-only. It does not attempt
to control a browser or solve access challenges; it classifies common visual
automation failures from sanitized run artifacts.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


VISUAL_FAILURE_TYPES = {
    "overlay_blocked": "Modal, overlay, or dialog blocks the target element",
    "dom_locator_missing": "Target DOM node is missing, stale, or not interactable",
    "viewport_scale_drift": "Device scale factor or viewport scaling caused coordinate drift",
    "screenshot_not_loaded": "Screenshot was captured before the page finished loading",
    "ocr_mismatch": "OCR output is ambiguous or likely misread",
    "coordinate_drift": "Recorded click coordinates do not hit the target bounding box",
    "screenshot_dom_inconsistency": "Screenshot and DOM visibility state are inconsistent",
    "unknown_visual": "Insufficient visual evidence for a specific diagnosis",
}


def diagnose_visual_failure(artifact_dir: str | Path) -> dict[str, Any]:
    """Diagnose visual/browser automation failures from a local artifact folder."""
    path = Path(artifact_dir)
    findings: list[str] = []
    failure_types: list[str] = []
    confidence = 0.45

    has_screenshot = (path / "screenshot.png").exists()
    has_dom = (path / "dom_snapshot.html").exists()
    has_coords = (path / "click_coordinates.json").exists()
    has_ocr = (path / "ocr_excerpt.txt").exists()
    has_trace = (path / "trace.zip").exists()

    evidence_count = sum([has_screenshot, has_dom, has_coords, has_ocr, has_trace])

    if has_dom:
        dom_text = (path / "dom_snapshot.html").read_text(encoding="utf-8", errors="ignore").lower()
        _detect_dom_visual_failures(dom_text, failure_types, findings)
        if "overlay_blocked" in failure_types:
            confidence = max(confidence, 0.88)
        if "dom_locator_missing" in failure_types:
            confidence = max(confidence, 0.91)
        if "screenshot_not_loaded" in failure_types:
            confidence = max(confidence, 0.82)

    if has_coords:
        confidence = max(confidence, _detect_coordinate_failures(path / "click_coordinates.json", failure_types, findings))

    if has_ocr:
        confidence = max(confidence, _detect_ocr_failures(path / "ocr_excerpt.txt", failure_types, findings))

    if has_screenshot and has_dom:
        dom_text = (path / "dom_snapshot.html").read_text(encoding="utf-8", errors="ignore").lower()
        if "display:none" in dom_text or "display: none" in dom_text or "visibility:hidden" in dom_text:
            failure_types.append("screenshot_dom_inconsistency")
            findings.append(
                "DOM contains hidden target evidence (display:none or visibility:hidden), "
                "so screenshot-visible state may not match interactable DOM state."
            )
            confidence = max(confidence, 0.87)
        else:
            findings.append("DOM visibility hints do not show a screenshot/DOM inconsistency.")

    if not failure_types:
        failure_types = ["unknown_visual"]
        if evidence_count == 0:
            findings.append("No visual evidence files were found.")
        else:
            findings.append("Visual evidence was present but no known visual failure pattern matched.")

    ordered = _ordered_unique(failure_types)
    primary_type = _choose_primary_type(ordered)
    description = VISUAL_FAILURE_TYPES.get(primary_type, VISUAL_FAILURE_TYPES["unknown_visual"])

    missing_evidence = []
    if not has_screenshot:
        missing_evidence.append("screenshot.png")
    if not has_dom:
        missing_evidence.append("dom_snapshot.html")
    if not has_coords:
        missing_evidence.append("click_coordinates.json")
    if not has_ocr:
        missing_evidence.append("ocr_excerpt.txt")
    if not has_trace:
        missing_evidence.append("trace.zip")

    return {
        "diagnosis_type": "visual_failure",
        "primary_failure_type": primary_type,
        "all_failure_types": ordered,
        "description": description,
        "confidence": confidence,
        "confidence_label": f"{confidence:.0%}",
        "findings": findings,
        "evidence_files_present": {
            "screenshot.png": has_screenshot,
            "dom_snapshot.html": has_dom,
            "click_coordinates.json": has_coords,
            "ocr_excerpt.txt": has_ocr,
            "trace.zip": has_trace,
        },
        "missing_evidence": missing_evidence,
        "recommendations": _build_visual_recommendations(ordered),
    }


def _detect_dom_visual_failures(dom_text: str, failure_types: list[str], findings: list[str]) -> None:
    overlay_patterns = [
        'class="modal',
        "class='modal",
        'class="overlay',
        "class='overlay",
        'class="popup',
        "class='popup",
        'style="display:block',
        'style="display: block',
        "z-index:9",
        "z-index: 9",
        'aria-modal="true',
        "aria-modal='true",
        'role="dialog',
        "role='dialog",
        'role="alertdialog',
        "role='alertdialog",
        "backdrop",
        "dimmer",
        "mask",
        "dialog open",
    ]
    overlay_hits = [pattern for pattern in overlay_patterns if pattern in dom_text]
    if overlay_hits:
        failure_types.append("overlay_blocked")
        findings.append(f"Overlay/dialog evidence matched {len(overlay_hits)} DOM hints: {overlay_hits[:3]}.")

    locator_absent_hints = [
        "no such element",
        "element not found",
        "elementnotvisibleexception",
        "elementnotinteractable",
        "strict mode violation",
        "detached from document",
    ]
    locator_hits = [hint for hint in locator_absent_hints if hint in dom_text]
    if locator_hits:
        failure_types.append("dom_locator_missing")
        findings.append(f"DOM/locator failure hints matched: {locator_hits[:2]}.")

    loading_hints = [
        "loading...",
        "skeleton",
        "spinner",
        'data-loading="true"',
        "data-loading='true'",
        'aria-busy="true"',
        "aria-busy='true'",
        "placeholder shimmer",
    ]
    loading_hits = [hint for hint in loading_hints if hint in dom_text]
    if loading_hits:
        failure_types.append("screenshot_not_loaded")
        findings.append(f"Loading-state evidence matched: {loading_hits[:2]}.")


def _detect_coordinate_failures(coords_file: Path, failure_types: list[str], findings: list[str]) -> float:
    confidence = 0.45
    try:
        coords_data = json.loads(coords_file.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser errors are not important
        findings.append(f"Could not parse click_coordinates.json: {exc}")
        return confidence

    device_scale = float(coords_data.get("device_scale_factor", 1.0) or 1.0)
    click_x = float(coords_data.get("click_x", 0) or 0)
    click_y = float(coords_data.get("click_y", 0) or 0)
    target_bbox = coords_data.get("target_bounding_box")

    if device_scale != 1.0:
        failure_types.append("viewport_scale_drift")
        findings.append(
            f"device_scale_factor={device_scale} differs from 1.0; coordinate math may be scaled incorrectly."
        )
        confidence = max(confidence, 0.85)

    if isinstance(target_bbox, dict):
        bbox_x = float(target_bbox.get("x", 0) or 0)
        bbox_y = float(target_bbox.get("y", 0) or 0)
        bbox_w = float(target_bbox.get("width", 1) or 1)
        bbox_h = float(target_bbox.get("height", 1) or 1)
        in_bounds = bbox_x <= click_x <= bbox_x + bbox_w and bbox_y <= click_y <= bbox_y + bbox_h
        if not in_bounds:
            failure_types.append("coordinate_drift")
            findings.append(
                f"Click point ({click_x:g},{click_y:g}) is outside target bounding box "
                f"[{bbox_x:g},{bbox_y:g},{bbox_x + bbox_w:g},{bbox_y + bbox_h:g}]."
            )
            confidence = max(confidence, 0.93)
        else:
            findings.append("Click coordinates fall inside the target bounding box.")

    return confidence


def _detect_ocr_failures(ocr_file: Path, failure_types: list[str], findings: list[str]) -> float:
    ocr_text = ocr_file.read_text(encoding="utf-8", errors="ignore")
    common_ocr_errors = [
        (r"\b[0O][\d]{3,}\b", "digit 0 and letter O may be confused"),
        (r"\b[lI1]{2,}\b", "digit 1 and letters I/l may be confused"),
        (r"[$]\s+\d", "currency symbol spacing is suspicious"),
        (r"\?\?+", "unrecognized OCR characters"),
        (r"\ufffd+", "replacement characters in OCR output"),
    ]
    for pattern, description in common_ocr_errors:
        if re.search(pattern, ocr_text):
            failure_types.append("ocr_mismatch")
            findings.append(f"OCR anomaly detected: {description}.")
            return 0.79
    findings.append("OCR excerpt does not contain a known ambiguity pattern.")
    return 0.45


def _choose_primary_type(failure_types: list[str]) -> str:
    priority = [
        "overlay_blocked",
        "coordinate_drift",
        "viewport_scale_drift",
        "screenshot_not_loaded",
        "screenshot_dom_inconsistency",
        "dom_locator_missing",
        "ocr_mismatch",
        "unknown_visual",
    ]
    for item in priority:
        if item in failure_types:
            return item
    return failure_types[0] if failure_types else "unknown_visual"


def _ordered_unique(values: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _build_visual_recommendations(failure_types: list[str]) -> list[str]:
    """Return actionable, public-safe recommendations for detected visual failures."""
    recs = []
    if "overlay_blocked" in failure_types:
        recs.append("Wait for or close blocking modals/overlays before clicking the target element.")
    if "dom_locator_missing" in failure_types:
        recs.append("Verify the selector against the latest DOM and wait for the locator before interaction.")
    if "viewport_scale_drift" in failure_types:
        recs.append("Normalize device_scale_factor or use locator-based interactions instead of raw coordinates.")
    if "screenshot_not_loaded" in failure_types:
        recs.append("Capture screenshots after a stable load signal such as network idle or a domain-specific ready marker.")
    if "ocr_mismatch" in failure_types:
        recs.append("Prefer DOM-accessible text when available; otherwise capture higher-quality screenshots for OCR.")
    if "coordinate_drift" in failure_types:
        recs.append("Use element-based clicks or recompute coordinates after scrolling and viewport changes.")
    if "screenshot_dom_inconsistency" in failure_types:
        recs.append("Check CSS visibility/interactability before assuming a screenshot-visible element is clickable.")
    if not recs:
        recs.append("Collect screenshot.png, dom_snapshot.html, click_coordinates.json, and OCR text before hard classification.")
    return recs


def run_visual_diagnosis_cli(artifact_dir: str) -> None:
    """Print a compact visual diagnosis summary."""
    result = diagnose_visual_failure(artifact_dir)
    print("\n" + "=" * 60)
    print("Visual Failure Doctor")
    print("=" * 60)
    print(f"Primary failure type: {result['primary_failure_type']}")
    print(f"Description: {result['description']}")
    print(f"Confidence: {result['confidence_label']}")
    print(f"\nFindings ({len(result['findings'])}):")
    for finding in result["findings"]:
        print(f"  {finding}")
    if result["recommendations"]:
        print(f"\nRecommendations ({len(result['recommendations'])}):")
        for recommendation in result["recommendations"]:
            print(f"  {recommendation}")
    if result["missing_evidence"]:
        print(f"\nMissing evidence: {', '.join(result['missing_evidence'])}")
    print("=" * 60)
