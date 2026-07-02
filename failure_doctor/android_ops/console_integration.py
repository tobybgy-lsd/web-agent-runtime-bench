from __future__ import annotations

from .ops_dashboard import android_ops_dashboard_summary


def android_ops_console_summary() -> dict:
    payload = android_ops_dashboard_summary()
    payload["console_integration"] = "available"
    payload["local_only"] = True
    return payload

