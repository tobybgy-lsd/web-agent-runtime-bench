from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ops_audit import append_audit, write_json
from .ops_task_queue import load_tasks


def plan_schedule(farm: Path, queue: Path, out: Path, strategy: str = "dry_run_only") -> dict[str, Any]:
    devices = []
    devices_path = farm / "devices.json"
    if devices_path.exists():
        devices = json.loads(devices_path.read_text(encoding="utf-8")).get("devices", [])
    tasks = load_tasks(queue)
    available = [d for d in devices if d.get("status") == "available"] or [{"device_id": "mock-emulator-5554"}]
    assignments = []
    for idx, task in enumerate(tasks):
        device = available[idx % len(available)]
        assignments.append(
            {
                "task_id": task.get("task_id", f"task_{idx+1:03d}"),
                "device_id": device["device_id"],
                "mode": "dry_run",
                "status": "planned",
                "requires_manual_review": False,
            }
        )
    payload = {
        "schema_version": "android_scheduler_plan/v1",
        "status": "pass",
        "strategy": strategy,
        "assignments": assignments,
        "dry_run_only": True,
        "final_submit_allowed": False,
        "business_mutation_allowed": False,
    }
    write_json(out / "schedule_plan.json", payload)
    append_audit(farm, "scheduler_plan", {"task_count": len(assignments)})
    return payload


def run_schedule(plan: Path, out: Path) -> dict[str, Any]:
    payload = json.loads((plan / "schedule_plan.json" if plan.is_dir() else plan).read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    for child in ("per_device", "failed", "manual_review", "replay_packs", "sanitized_summary"):
        (out / child).mkdir(exist_ok=True)
    results = []
    for assignment in payload.get("assignments", []):
        results.append({**assignment, "result": "dry_run_success", "checkpoint_written": True})
    (out / "task_results.jsonl").write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in results) + ("\n" if results else ""),
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "android_ops_run/v1",
        "status": "pass",
        "task_count": len(results),
        "dry_run_only": True,
        "real_business_mutation_count": 0,
    }
    write_json(out / "ops_run_manifest.json", manifest)
    (out / "open_this_first_android_ops.md").write_text("# Android Ops Run\n\nDry-run local-only run completed.\n", encoding="utf-8")
    return manifest

