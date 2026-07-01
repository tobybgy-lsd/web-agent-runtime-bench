from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import VisualRun


def screenshot_cost_report(run: VisualRun) -> dict[str, Any]:
    frames = run.screenshots_manifest.get("frames", [])
    costs: list[dict[str, Any]] = []
    total_bytes = 0
    total_tokens = 0
    for frame in frames:
        if not isinstance(frame, dict):
            continue
        rel = str(frame.get("path", ""))
        size = int(frame.get("byte_size") or _file_size(run.root / rel))
        width = int(frame.get("width") or 0)
        height = int(frame.get("height") or 0)
        tokens = int(frame.get("estimated_image_tokens") or max(1, (width * height) // 768))
        quality = float(frame.get("quality_score", 0.85))
        total_bytes += size
        total_tokens += tokens
        costs.append(
            {
                "step_id": frame.get("step_id"),
                "path": rel,
                "byte_size": size,
                "estimated_image_tokens": tokens,
                "quality_score": quality,
                "overcompressed": bool(frame.get("overcompressed") or quality < 0.45),
                "underloaded": bool(frame.get("underloaded") or size <= 0),
                "capture_latency_ms": frame.get("capture_latency_ms", 0),
                "encode_latency_ms": frame.get("encode_latency_ms", 0),
                "decode_latency_ms": frame.get("decode_latency_ms", 0),
            }
        )
    return {
        "schema_version": "screenshot_cost_report/v1",
        "frame_count": len(costs),
        "total_bytes": total_bytes,
        "total_estimated_image_tokens": total_tokens,
        "image_token_budget_exceeded": total_tokens > int(run.manifest.get("image_token_budget", 8000)),
        "transport_overhead_score": round(min(1.0, total_bytes / 5_000_000), 3),
        "frames": costs,
    }


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0
