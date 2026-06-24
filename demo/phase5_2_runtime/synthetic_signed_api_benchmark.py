#!/usr/bin/env python
"""Phase 5.2-A3: Synthetic Signed API Benchmark — mock verification.

Provides: stable_json, compute_demo_signature_v2, verify_signed_api_case,
build_negative_cases.
All operations are local/synthetic only. No real platforms.
"""

from __future__ import annotations

import hashlib
import json


ALLOWED_PATH_PREFIX = "/local/mock/signed-api/"
HEADER_NAME = "x-demo-signature"


def stable_json(obj: dict) -> str:
    """JSON stringify with sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_demo_signature_v2(case_name: str, request: dict, dependencies: dict) -> str:
    """Compute WARBDemoV2 signature matching JS bundle algorithm."""
    seed_parts = [
        "WARBDemoV2",
        case_name,
        request.get("method", "GET"),
        request.get("path", "/"),
        stable_json(request.get("payload", {})),
        str(dependencies.get("timestamp", "") or ""),
        str(dependencies.get("nonce", "") or ""),
        str(dependencies.get("user_agent", "") or ""),
        str(dependencies.get("salt_source", "") or ""),
        str(dependencies.get("document_meta_token", "") or ""),
        str(dependencies.get("event_token", "") or ""),
    ]
    seed = "|".join(seed_parts)
    return "demo_" + _sha256(seed)


def verify_signed_api_case(
    case_name: str, request: dict, headers: dict, dependencies: dict
) -> dict:
    """Verify x-demo-signature against WARBDemoV2 expectation.

    Returns:
      {"accepted": bool, "reason": str, "case_name": str, "synthetic_only": True}
    """
    path = request.get("path", "")
    if not path.startswith(ALLOWED_PATH_PREFIX):
        return {
            "accepted": False,
            "reason": f"path not under {ALLOWED_PATH_PREFIX}",
            "case_name": case_name,
            "synthetic_only": True,
        }

    received_sig = headers.get(HEADER_NAME, "")
    if not received_sig:
        return {
            "accepted": False,
            "reason": "missing x-demo-signature header",
            "case_name": case_name,
            "synthetic_only": True,
        }

    expected_sig = compute_demo_signature_v2(case_name, request, dependencies)

    if received_sig == expected_sig:
        return {
            "accepted": True,
            "reason": "signature_match",
            "case_name": case_name,
            "synthetic_only": True,
        }
    else:
        return {
            "accepted": False,
            "reason": "signature_mismatch",
            "case_name": case_name,
            "synthetic_only": True,
        }


def build_negative_cases(case_result: dict) -> list[dict]:
    """Generate negative (tampered) test cases for a valid signed request.

    Creates one tampered-payload negative case.
    """
    original_request = case_result.get("request", {})
    original_deps = case_result.get("dependencies", {})
    tampered_payload = dict(original_request.get("payload", {}))
    tampered_payload["tampered"] = True

    negative = {
        "negative_type": "tampered_payload",
        "case_name": case_result["case_name"],
        "original_signature": case_result.get("signature", ""),
        "request": {**original_request, "payload": tampered_payload},
        "dependencies": original_deps,
    }
    return [negative]
