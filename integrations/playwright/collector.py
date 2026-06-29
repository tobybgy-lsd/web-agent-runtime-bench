from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from integrations._pack import evidence_summary, first_text_file, reset_dir, write_json, write_text


def collect_playwright_artifacts(test_results: str | Path, out_dir: str | Path) -> dict[str, Any]:
    source = Path(test_results)
    out = Path(out_dir)
    if not source.exists():
        raise FileNotFoundError(source)
    reset_dir(out)

    trace = _first_match(source, "trace.zip")
    if trace:
        shutil.copy2(trace, out / "trace.zip")

    network = _first_match(source, "network.json")
    if network:
        shutil.copy2(network, out / "network.json")

    console = _first_match(source, "console.txt")
    if console:
        shutil.copy2(console, out / "console.txt")

    screenshot = _first_screenshot(source)
    if screenshot:
        shutil.copy2(screenshot, out / screenshot.name)

    error_source = first_text_file(source, ("error.log", "error-context.md", "stderr.txt"))
    error_text = error_source.read_text(encoding="utf-8", errors="replace") if error_source else _trace_error_hint(trace)
    write_text(out / "error.log", error_text or "Playwright test failed; inspect trace.zip and test-results artifacts.")

    write_text(
        out / "user_description.txt",
        "Collected from local Playwright test-results by Agent Failure Doctor. "
        "This pack is local-first and contains sanitized artifacts only.",
    )
    summary = {
        "adapter": "playwright",
        "source": str(source),
        **evidence_summary(out),
    }
    write_json(out / "input_summary.json", summary)
    return summary


def _first_match(root: Path, name: str) -> Path | None:
    for path in sorted(root.rglob(name)):
        if path.is_file():
            return path
    return None


def _first_screenshot(root: Path) -> Path | None:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            return path
    return None


def _trace_error_hint(trace: Path | None) -> str:
    if not trace:
        return ""
    return "Playwright trace.zip collected; no separate error log was found."

