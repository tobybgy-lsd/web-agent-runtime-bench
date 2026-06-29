from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from integrations._pack import evidence_summary, first_text_file, reset_dir, write_json, write_text


def pack_generic_logs(raw_logs: str | Path, out_dir: str | Path) -> dict[str, Any]:
    source = Path(raw_logs)
    out = Path(out_dir)
    if not source.exists():
        raise FileNotFoundError(source)
    reset_dir(out)

    error = first_text_file(source, ("error.log", "failure.log", "failure.txt", "stderr.txt"))
    if error:
        shutil.copy2(error, out / "error.log")
    else:
        write_text(out / "error.log", "No explicit error log found; inspect the original raw log folder.")

    for name in ("console.txt", "network.json", "user_description.txt", "README.txt"):
        match = _first_match(source, name)
        if match:
            shutil.copy2(match, out / name)

    if not (out / "user_description.txt").exists() and (out / "README.txt").exists():
        shutil.copy2(out / "README.txt", out / "user_description.txt")

    for screenshot in _screenshots(source):
        shutil.copy2(screenshot, out / screenshot.name)

    summary = {
        "adapter": "generic_log_pack",
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


def _screenshots(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ][:5]

