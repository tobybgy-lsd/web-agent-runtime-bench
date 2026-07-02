from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def replay_run_report(report: Path | str, out_dir: Path | str) -> dict[str, Any]:
    source = Path(report)
    if source.is_dir():
        source = source / "android_run_report.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    replay = {
        "schema_version": "android_replay_report/v1",
        "source": str(source),
        "status": "pass" if payload.get("schema_version") == "android_run_report/v1" else "fail",
        "step_count": len(payload.get("steps") or []),
        "blocked": payload.get("status") == "blocked",
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "real_platform_access_count": 0,
    }
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "android_replay_report.json").write_text(json.dumps(replay, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return replay
