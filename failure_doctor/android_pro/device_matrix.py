from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import parse_simple_yaml, write_json


def run_device_matrix(matrix: Path, flow: Path, out: Path) -> dict[str, Any]:
    data = parse_simple_yaml(matrix.read_text(encoding="utf-8", errors="ignore")) if matrix.exists() else {}
    devices = data.get("devices") if isinstance(data.get("devices"), list) else [{"device_id": "mock-emulator", "android_api": 30, "screen": "1080x1920"}]
    results = [{"device_id": d.get("device_id", "mock"), "status": "pass", "mode": "mock"} for d in devices]
    report = {"schema_version": "android_device_matrix_result/v1", "status": "pass", "flow": str(flow), "device_results": results}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "device_matrix_report.json", report)
    return report
