from __future__ import annotations

from typing import Any


def public_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": payload.get("status", "pass"),
        "local_only": True,
        "no_upload": True,
        "no_telemetry": True,
        "final_submit_default_blocked": True,
        "business_mutation_default_blocked": True,
    }

