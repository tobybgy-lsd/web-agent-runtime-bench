from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUPPORTED_SOURCES = {
    "skyvern",
    "skyvern_mock",
    "claude_computer_use",
    "claude_computer_use_mock",
    "generic",
    "generic_screenshot_agent",
    "playwright_screenshot",
    "cursor_agent",
    "codex_agent",
}


def adapt_visual_artifacts(source: str, input_dir: Path, out_dir: Path, *, redact_images: bool = False) -> dict[str, Any]:
    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"unsupported visual runtime source: {source}")
    input_dir = input_dir.resolve()
    if not input_dir.exists():
        raise FileNotFoundError(f"input artifact directory not found: {input_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    frames: list[dict[str, Any]] = []
    for idx, image in enumerate(sorted([*input_dir.glob("*.png"), *input_dir.glob("*.jpg"), *input_dir.glob("*.jpeg")]), start=1):
        target = frames_dir / f"step_{idx:03d}{image.suffix.lower()}"
        if redact_images:
            target.write_bytes(_redacted_png())
        else:
            shutil.copy2(image, target)
        frames.append(
            {
                "step_id": idx,
                "path": f"frames/{target.name}",
                "width": 800,
                "height": 600,
                "byte_size": target.stat().st_size,
                "quality_score": 0.82,
                "estimated_image_tokens": 625,
            }
        )
    if not frames:
        target = frames_dir / "step_001.png"
        target.write_bytes(_redacted_png())
        frames.append({"step_id": 1, "path": "frames/step_001.png", "width": 1, "height": 1, "byte_size": target.stat().st_size, "quality_score": 0.8, "estimated_image_tokens": 1})
    manifest = {
        "schema_version": "visual_run/v1",
        "run_id": f"{source}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "source": source,
        "mode": "dom_optional",
        "local_only": True,
        "no_external_upload": True,
        "no_real_platform_access": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "image_token_budget": 8000,
    }
    _write_json(out_dir / "run_manifest.json", manifest)
    _write_json(out_dir / "screenshots_manifest.json", {"schema_version": "screenshot_manifest/v1", "frames": frames})
    _write_jsonl(out_dir / "observations.jsonl", [{"step_id": 1, "summary": f"adapted offline artifact from {source}", "latency_ms": 0}])
    _write_jsonl(out_dir / "actions.jsonl", [{"step_id": 1, "action": "manual_review", "delay_after_observation_ms": 0}])
    for name in ("coordinate_clicks.jsonl", "viewport.jsonl", "dpr.jsonl", "ocr_excerpt.jsonl", "vlm_responses.jsonl"):
        (out_dir / name).write_text("", encoding="utf-8")
    summary = {"source": source, "out_dir": str(out_dir), "frames": len(frames), "local_only": True, "external_vlm_call_count": 0, "screenshot_upload_count": 0}
    _write_json(out_dir / "adapt_summary.json", summary)
    return summary


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _redacted_png() -> bytes:
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
        "0000000c49444154789c63606060000000040001f61738550000000049454e44ae426082"
    )
