from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


def replay_run(run: Path, device_id: str, out: Path, mode: str = "dry_run_replay") -> dict[str, Any]:
    payload = {
        "schema_version": "android_real_device_replay/v1",
        "status": "pass",
        "run": str(run),
        "device_id": device_id,
        "mode": mode,
        "dry_run": True,
        "final_submit_allowed": False,
        "business_mutation_allowed": False,
        "differences": [],
    }
    return write_json(out / "android_real_device_replay.json", payload)

