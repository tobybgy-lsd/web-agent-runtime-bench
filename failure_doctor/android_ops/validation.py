from __future__ import annotations

from typing import Any


def validate_android_ops_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "android_ops_validation_result/v1",
        "status": "pass" if payload.get("local_only", True) and payload.get("no_upload", True) else "fail",
        "checked": True,
    }

