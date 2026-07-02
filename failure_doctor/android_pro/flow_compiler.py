from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import read_flow, write_json
from .flow_linter import lint_flow_file


def compile_flow(flow: Path, profile: Path | None, out: Path) -> dict[str, Any]:
    lint = lint_flow_file(flow, profile, out)
    source = read_flow(flow)
    compiled = {
        "schema_version": "android_flow_compiled/v1",
        "status": "pass" if lint["status"] == "pass" else "blocked",
        "source_flow": str(flow),
        "profile": str(profile) if profile else None,
        "steps": source.get("steps", []),
        "lint": lint,
        "dry_run": True,
    }
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "compiled_flow.json", compiled)
    return compiled
