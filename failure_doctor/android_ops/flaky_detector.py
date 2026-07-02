from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .ops_audit import write_json


def detect_flaky(runs: Path, out: Path) -> dict[str, Any]:
    findings = []
    dimensions = Counter()
    for path in runs.rglob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        text = json.dumps(payload, ensure_ascii=False).lower()
        for key in ("device", "android_version", "locator", "permission", "network", "webview"):
            if key in text:
                dimensions[key] += 1
    for dimension, count in dimensions.items():
        if count:
            findings.append({"dimension": dimension, "count": count, "risk": "medium"})
    score = min(1.0, len(findings) / 6)
    payload = {
        "schema_version": "android_flaky_flow_report/v1",
        "status": "pass",
        "flaky_score": score,
        "flaky_findings": findings,
        "suspected_dimensions": [f["dimension"] for f in findings] or ["device", "locator"],
        "safe_next_actions": [
            "Compare sanitized replay packs across devices before changing the flow.",
            "Prefer stable resource-id or accessibility locators over coordinate fallbacks.",
            "Use manual review for uncertain task failures.",
        ],
    }
    return write_json(out / "android_flaky_flow_report.json", payload)

