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


def _demo_header_name(name: str) -> str:
    return "x-" + name


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


def classify_scraper_error(stderr: str, stdout: str = "", html: str = "") -> dict:
    """Extended classifier informed by local Spiderbuf-style training cases.

    Adds: HTTP error codes, CSS anti-crawl, Selenium/captcha, crypto failures,
    and HTML structure analysis. 35+ patterns with 80-95% confidence.

    Still pure rule matching. No model calls. No network.
    Public-safe validation covers diagnosis only. Private execution notes are not
    part of this public demo.
    """
    combined = f"{stderr}\n{stdout}".strip()
    lowered = combined.lower()
    if not combined:
        return _result("success", 1.0, "no error output", "no repair required")

    # === Spiderbuf-validated patterns ===

    # HTTP errors
    signature_header_needles = [
        "missing required headers",
        "missing header",
        "signature header",
        "timestamp header",
        "nonce header",
        _demo_header_name("timestamp"),
        _demo_header_name("nonce"),
        _demo_header_name("sign"),
    ]
    http_patterns = [
        ("signature_param_missing", 0.88,
         signature_header_needles,
         "Required request signature headers are missing. Inspect the page script for token/sign generation inputs before crypto-specific guesses."),
        ("http_403_forbidden", 0.92, ["403", "forbidden", "access denied"],
         "Server rejected request after request metadata checks. Verify permission, request headers, and official API availability."),
        ("http_429_rate_limit", 0.95, ["429", "too many requests", "rate limit"],
         "Request rate exceeded. Add time.sleep(2) between requests."),
        ("http_404_not_found", 0.95, ["404", "not found"],
         "URL does not exist. Check the endpoint path."),
    ]
    for error_type, conf, keywords, repair in http_patterns:
        if any(kw in lowered for kw in keywords):
            return _result(error_type, conf, combined, repair)

    # Selenium / browser automation
    selenium_patterns = [
        ("selenium_webdriver_detected", 0.92,
         ["navigator.webdriver", "webdriver detected", "automation detected",
          "chrome is being controlled by automated"],
         "Browser automation fingerprint risk detected. Treat as anti_bot_risk_boundary; use authorized testing hooks, public APIs, or manual verification."),
        ("anti_bot_risk_boundary", 0.90,
         ["slider", "slide", "nosuchelement", "captcha"],
         "Challenge/captcha/slider risk detected. Do not automate circumvention. Use manual verification, official API, approved workflow, or stop if not permitted."),
        ("anti_bot_risk_boundary", 0.82,
         ["mousemove", "behavior", "human verification", "are you a robot"],
         "Human-verification or behavior-risk signal detected. Do not provide evasion steps; use manual verification, official API, or approved workflow changes."),
    ]
    for error_type, conf, keywords, repair in selenium_patterns:
        if any(kw in lowered for kw in keywords):
            return _result(error_type, conf, combined, repair)

    # Crypto / signature errors
    crypto_patterns = [
        ("aes_decrypt_failed", 0.88,
         ["aes", "cryptojs", "bad decrypt", "pad block corrupted", "invalid key size"],
         "AES decryption failed. Check: mode (CBC/ECB), IV position (first 16 bytes?), PKCS7 padding."),
        ("md5_signature_failed", 0.88,
         ["md5", "hash mismatch", "invalid hash"],
         "MD5 signature mismatch. Check parameter concatenation format and timestamp precision."),
        ("hmac_signature_failed", 0.86,
         ["hmac", "signature mismatch", "signature verification failed"],
         "HMAC signature failed. Verify algorithm (SHA256), message order, and key source."),
        ("base64_decode_failed", 0.92,
         ["base64", "incorrect padding", "invalid base64"],
         "Base64 decode failed. Check if data needs URL-decode or data: URI prefix removal first."),
    ]
    for error_type, conf, keywords, repair in crypto_patterns:
        if any(kw in lowered for kw in keywords):
            return _result(error_type, conf, combined, repair)

    # CSS/lxml parsing errors
    parsing_patterns = [
        ("nested_text_failed", 0.85,
         [".text", "nonetype", "has no attribute"],
         "td.text returned None. Text is in child tags (<a>/<font>/<span>). Use xpath('string(.)') instead."),
        ("css_pseudo_element", 0.80,
         ["indexerror", "list index out of range"],
         "CSS pseudo-element obfuscation suspected. Parse ::before/::after content from CSS stylesheet."),
    ]
    for error_type, conf, keywords, repair in parsing_patterns:
        if any(kw in lowered for kw in keywords):
            return _result(error_type, conf, combined, repair)

    # HTML content analysis (when stderr is empty but extraction failed)
    if html:
        if "::before" in html or "::after" in html:
            return _result("css_pseudo_element_detected", 0.90, "HTML contains ::before/::after rules",
                          "Parse CSS stylesheet for class→content mapping, then decode by class order")
        if "sprite" in html.lower() and "background" in html.lower():
            return _result("css_sprite_detected", 0.88, "CSS sprite anti-crawl detected",
                          "Extract sprite class→digit mapping from CSS background-position rules")
        if "debugger" in html.lower():
            return _result("anti_debug_detected", 0.90, "setInterval debugger detected",
                          "Use Selenium with page_source extraction instead of requests")
        if any(kw in html.lower() for kw in ["cryptojs", "aes.decrypt"]):
            return _result("crypto_js_required", 0.85, "CryptoJS/AES encryption detected",
                          "Client-side crypto/signature logic detected. Diagnose parameter mismatch and use authorized API docs or owner-provided test hooks.")
        if "worker" in html.lower():
            return _result("web_worker_detected", 0.82, "Web Worker detected",
                          "Worker-based anti-debug or dynamic rendering detected. Capture more evidence and avoid bypass-oriented interception guidance.")
        challenge_markers = [
            "just a moment",
            "checking your browser",
            "settimeout",
            "location.reload",
            "clearance",
            "md5",
            "salt",
        ]
        if ("503" in lowered or "service unavailable" in lowered) and sum(1 for marker in challenge_markers if marker in html.lower()) >= 3:
            return _result(
                "challenge_page_detected",
                0.92,
                "HTTP 503 challenge page with delayed script and browser state marker",
                "Challenge page detected. Treat as anti_bot_risk_boundary; use manual verification, official API, approved workflow, or stop if not permitted.",
            )

    # Fallback to existing classifier for runtime errors
    existing = classify_runtime_error(stderr, stdout)
    if existing["error_type"] != "unknown_runtime_error":
        return existing

    return _result("unknown_scraper_error", 0.30, combined,
                   "No pattern matched. Inspect error log and add new classifier rule.")
