from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .flow import load_flow, validate_flow
from .safety import evaluate_flow_safety


def run_flow_file(path: Path | str, out_dir: Path | str, *, dry_run: bool = True) -> dict[str, Any]:
    flow = load_flow(path)
    validation = validate_flow(flow)
    safety = evaluate_flow_safety(flow)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    steps = []
    blocked = safety["status"] == "blocked"
    for index, step in enumerate(flow.get("steps") or []):
        step_status = "blocked" if blocked else "dry_run_skipped" if dry_run else "ready_for_authorized_runner"
        steps.append(
            {
                "index": index,
                "id": step.get("id", f"step_{index}"),
                "action": step.get("action"),
                "status": step_status,
                "locator": step.get("locator", {}),
                "final_submit": bool(step.get("final_submit")),
            }
        )
    payload = {
        "schema_version": "android_run_report/v1",
        "flow_id": flow.get("flow_id"),
        "status": "blocked" if blocked else "pass",
        "dry_run": dry_run,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validation": validation,
        "safety": safety,
        "steps": steps,
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
    }
    (output / "android_run_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
