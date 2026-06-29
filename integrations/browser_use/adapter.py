from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from integrations._pack import evidence_summary, reset_dir, write_json, write_text


def convert_browser_use_run(input_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    source = Path(input_path)
    out = Path(out_dir)
    if not source.exists():
        raise FileNotFoundError(source)
    reset_dir(out)

    if source.suffix.lower() == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
        error_text = _error_from_history(data)
        steps = _steps_from_history(data)
    else:
        data = {"log": source.read_text(encoding="utf-8", errors="replace")}
        error_text = str(data["log"])
        steps = _steps_from_log(error_text)

    write_text(out / "error.log", error_text)
    write_text(
        out / "user_description.txt",
        "Converted from a local browser-use or browser-agent run. "
        "Diagnose the failure evidence and keep recommendations bounded to authorized debugging.",
    )
    write_json(out / "agent_steps.json", steps)
    summary = {
        "adapter": "browser_use",
        "source": str(source),
        "detected_markers": _detected_markers(error_text),
        **evidence_summary(out),
    }
    write_json(out / "input_summary.json", summary)
    return summary


def _error_from_history(data: Any) -> str:
    if not isinstance(data, dict):
        return "browser-use history is not a JSON object"
    for key in ("final_error", "error", "last_error"):
        if data.get(key):
            return str(data[key])
    steps = data.get("steps")
    if isinstance(steps, list):
        errors = []
        for step in steps:
            if isinstance(step, dict) and step.get("error"):
                errors.append(str(step["error"]))
        if errors:
            return "\n".join(errors)
    return json.dumps(data, ensure_ascii=False)[:2000]


def _steps_from_history(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("steps"), list):
        return [step for step in data["steps"] if isinstance(step, dict)]
    return []


def _steps_from_log(text: str) -> list[dict[str, Any]]:
    return [{"line": line} for line in text.splitlines()[:50] if line.strip()]


def _detected_markers(text: str) -> list[str]:
    lowered = text.lower()
    markers = []
    for marker in (
        "download not saved",
        "cdp websocket",
        "repeatedly executed",
        "target page, context or browser has been closed",
        "runtime api",
        "modulenotfounderror",
    ):
        if marker in lowered:
            markers.append(marker)
    return markers

