#!/usr/bin/env python
"""Rule-based classifier for synthetic browser runtime failures."""

from __future__ import annotations


def _result(error_type: str, confidence: float, evidence: str, recommended_patch: str) -> dict:
    return {
        "error_type": error_type,
        "confidence": confidence,
        "evidence": evidence[:240],
        "recommended_patch": recommended_patch,
        "synthetic_only": True,
    }


def classify_runtime_error(stderr: str, stdout: str = "") -> dict:
    """Classify Node stdout/stderr from the synthetic runtime demo.

    This is pure local rule matching. It does not call a model or the network.
    """

    combined = f"{stderr}\n{stdout}".strip()
    lowered = combined.lower()
    if not combined:
        return _result("success", 1.0, "no stderr/stdout error text", "no patch required")

    checks = [
        ("missing_window", "window is not defined", "apply synthetic_browser_shim.js to provide globalThis.window"),
        ("missing_document", "document is not defined", "apply synthetic_browser_shim.js to provide globalThis.document"),
        ("missing_navigator", "navigator is not defined", "apply synthetic_browser_shim.js to provide globalThis.navigator"),
        ("missing_event_target", "eventtarget is not defined", "apply synthetic_browser_shim.js to provide EventTarget"),
        ("missing_local_storage", "localstorage is not defined", "apply synthetic_browser_shim.js to provide localStorage"),
        ("missing_element", "element is not defined", "apply synthetic_browser_shim.js to provide Element"),
        ("missing_node", "node is not defined", "apply synthetic_browser_shim.js to provide Node"),
    ]
    for error_type, needle, patch in checks:
        if needle in lowered:
            return _result(error_type, 0.93, combined, patch)

    # Fallback: broader patterns
    broad_checks = [
        ("missing_window", "window", "referenceerror"),
        ("missing_document", "document", "referenceerror"),
        ("missing_navigator", "navigator", "referenceerror"),
        ("missing_event_target", "eventtarget", "referenceerror"),
        ("missing_local_storage", "localstorage", "referenceerror"),
    ]
    for error_type, needle, ref_key in broad_checks:
        if needle in lowered and ref_key in lowered:
            return _result(error_type, 0.85, combined, "apply synthetic_browser_shim.js (broad match)")

    if "typeerror" in lowered and "getitem" in lowered and "warb_demo_salt" in lowered:
        return _result(
            "missing_local_storage",
            0.86,
            combined,
            "apply synthetic_browser_shim.js to provide localStorage.getItem/setItem",
        )

    if "__warb_demo_sign" in combined and ("not a function" in lowered or "undefined" in lowered):
        return _result(
            "signature_function_missing",
            0.9,
            combined,
            "load synthetic_obfuscated_bundle.js after the synthetic browser shim",
        )
    if "syntaxerror" in lowered:
        return _result("syntax_error", 0.88, combined, "inspect synthetic JS syntax")
    if "typeerror" in lowered:
        return _result("runtime_type_error", 0.75, combined, "inspect shim surface and bundle assumptions")
    return _result("unknown_runtime_error", 0.35, combined, "capture stderr/stdout and add a local classifier rule")
