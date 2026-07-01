from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import VISUAL_SCHEMA_VERSION, VisualRun


JSONL_FILES = {
    "observations": "observations.jsonl",
    "actions": "actions.jsonl",
    "clicks": "coordinate_clicks.jsonl",
    "viewports": "viewport.jsonl",
    "dpr": "dpr.jsonl",
    "ocr": "ocr_excerpt.jsonl",
    "vlm_responses": "vlm_responses.jsonl",
}


def load_visual_run(path: Path, *, no_dom: bool = False, dom_optional: bool = False) -> VisualRun:
    root = path.resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"visual run directory not found: {root}")
    manifest = _read_json(root / "run_manifest.json")
    screenshots = _read_json(root / "screenshots_manifest.json")
    if manifest.get("schema_version") != VISUAL_SCHEMA_VERSION:
        raise ValueError("run_manifest.json must use schema_version visual_run/v1")
    if manifest.get("local_only") is not True or manifest.get("no_external_upload") is not True:
        raise ValueError("visual runs must declare local_only and no_external_upload")

    payload: dict[str, Any] = {}
    for key, filename in JSONL_FILES.items():
        payload[key] = _read_jsonl(root / filename)
    dom_dir = root / "dom_snapshots"
    dom_files = [] if no_dom else sorted(dom_dir.glob("*.html")) if dom_dir.exists() else []
    if not no_dom and not dom_optional and manifest.get("mode") == "visual_plus_dom" and not dom_files:
        raise ValueError("DOM snapshots are required for visual_plus_dom unless --dom-optional is used")
    return VisualRun(root=root, manifest=manifest, screenshots_manifest=screenshots, dom_snapshots=dom_files, **payload)


def validate_visual_run(path: Path, *, no_dom: bool = False, dom_optional: bool = False) -> dict[str, Any]:
    try:
        run = load_visual_run(path, no_dom=no_dom, dom_optional=dom_optional)
    except Exception as exc:  # noqa: BLE001 - validation report should carry the reason.
        return {
            "schema_version": "visual_runtime_validation/v1",
            "status": "fail",
            "errors": [str(exc)],
            "warnings": [],
        }
    warnings: list[str] = []
    frame_count = len(run.screenshots_manifest.get("frames", []))
    if frame_count == 0:
        warnings.append("no screenshot frames listed")
    return {
        "schema_version": "visual_runtime_validation/v1",
        "status": "pass" if frame_count else "warning",
        "errors": [],
        "warnings": warnings,
        "run_id": run.manifest.get("run_id"),
        "source": run.manifest.get("source"),
        "mode": run.manifest.get("mode"),
        "frame_count": frame_count,
        "observation_count": len(run.observations),
        "action_count": len(run.actions),
        "click_count": len(run.clicks),
        "dom_snapshot_count": len(run.dom_snapshots),
        "local_only": run.manifest.get("local_only") is True,
        "external_vlm_call_count": 0,
        "screenshot_upload_count": 0,
        "real_platform_access_count": 0,
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required visual runtime file missing: {path.name}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            rows.append(item)
    return rows
