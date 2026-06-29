from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


TEXT_EXTENSIONS = {".log", ".txt", ".md"}
SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def copy_first(paths: list[Path], dest: Path) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            shutil.copy2(path, dest)
            return dest
    return None


def copy_optional(path: Path, dest: Path) -> Path | None:
    if path.exists() and path.is_file():
        shutil.copy2(path, dest)
        return dest
    return None


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def evidence_summary(out_dir: Path) -> dict[str, Any]:
    files = {path.name.lower(): path for path in out_dir.iterdir() if path.is_file()}
    observed = {
        "trace_zip": 1 if "trace.zip" in files else 0,
        "logs": 1 if "error.log" in files else 0,
        "console": 1 if "console.txt" in files else 0,
        "network": 1 if "network.json" in files else 0,
        "description": 1 if "user_description.txt" in files or "readme.txt" in files else 0,
        "screenshots": len([name for name in files if Path(name).suffix.lower() in SCREENSHOT_EXTENSIONS]),
    }
    priority: list[str] = []
    if observed["trace_zip"]:
        priority.append("trace_zip")
    if observed["logs"]:
        priority.append("log")
    if observed["network"]:
        priority.append("network")
    if observed["description"]:
        priority.append("description")
    if observed["screenshots"]:
        priority.append("screenshot_metadata")
    missing = []
    if not observed["trace_zip"]:
        missing.append("trace_zip")
    if not observed["logs"]:
        missing.append("error.log")
    if not observed["network"]:
        missing.append("network.json")
    if not observed["description"]:
        missing.append("user_description.txt")
    if not observed["screenshots"]:
        missing.append("screenshot.png")
    return {
        "observed_evidence": observed,
        "evidence_priority": priority,
        "missing_evidence": missing,
        "recognized_files": sorted(path.name for path in out_dir.iterdir() if path.is_file()),
    }


def first_text_file(root: Path, names: tuple[str, ...] = ()) -> Path | None:
    lowered = {name.lower() for name in names}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name.lower() in lowered:
            return path
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            return path
    return None

