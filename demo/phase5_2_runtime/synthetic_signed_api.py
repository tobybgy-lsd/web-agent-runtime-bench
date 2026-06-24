#!/usr/bin/env python
"""Local mock signed API for Phase 5.2 synthetic runtime demo."""

from __future__ import annotations

import hashlib
import json

ALLOWED_PATH = "/local/mock/signed-api"
HEADER_NAME = "x-demo-signature"
ALGORITHM_MARKER = "WARBDemoV1"


def stable_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_demo_signature(path: str, payload: dict, user_agent: str, salt: str) -> str:
    text = f"{ALGORITHM_MARKER}|{path}|{stable_json(payload)}|{user_agent}|{salt}"
    return "demo_" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_demo_signed_request(path: str, payload: dict, headers: dict, dependencies: dict) -> dict:
    """Verify a local-only x-demo-signature header."""

    if path != ALLOWED_PATH:
        return {
            "accepted": False,
            "reason": "path_not_allowed_for_synthetic_mock",
            "expected_prefix": "demo_",
            "received_header": headers.get(HEADER_NAME, ""),
            "synthetic_only": True,
        }
    received = headers.get(HEADER_NAME, "")
    user_agent = dependencies.get("user_agent", "")
    salt = dependencies.get("salt", "synthetic_salt_v1")
    expected = compute_demo_signature(path, payload, user_agent, salt)
    accepted = received == expected
    return {
        "accepted": accepted,
        "reason": "signature_match" if accepted else "signature_mismatch",
        "expected_prefix": "demo_",
        "received_header": received,
        "synthetic_only": True,
    }
