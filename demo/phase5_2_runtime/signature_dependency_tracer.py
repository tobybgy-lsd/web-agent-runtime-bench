#!/usr/bin/env python
"""Trace synthetic signature dependencies without recording secrets."""

from __future__ import annotations


def _preview(value: object) -> str:
    text = "" if value is None else str(value)
    return text[:80]


def trace_signature_dependencies(sign_result: dict) -> dict:
    deps = sign_result.get("dependencies", {})
    items = [
        {"name": "path", "source": "runner_input", "value_preview": _preview(deps.get("path"))},
        {
            "name": "payload_hash",
            "source": "stable_json_payload",
            "value_preview": _preview(deps.get("payload_hash")),
        },
        {
            "name": "user_agent",
            "source": "synthetic_navigator",
            "value_preview": _preview(deps.get("user_agent")),
        },
        {
            "name": "salt",
            "source": "synthetic_localStorage",
            "value_preview": _preview(deps.get("salt_source", "localStorage.warb_demo_salt")),
        },
        {
            "name": "algorithm",
            "source": "synthetic_bundle",
            "value_preview": _preview(deps.get("algorithm", "WARBDemoV1")),
        },
    ]
    return {
        "dependency_count": len(items),
        "dependencies": items,
        "synthetic_only": True,
    }
