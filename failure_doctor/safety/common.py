from __future__ import annotations

from pathlib import Path
from typing import Iterable


TEXT_SUFFIXES = {
    ".bat",
    ".cfg",
    ".csv",
    ".diff",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".patch",
    ".ps1",
    ".py",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}


def iter_text_files(root: Path, limit: int = 500) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in TEXT_SUFFIXES or root.name.lower() in {"cookies", "login data", "local state"}:
            yield root
        return
    count = 0
    for path in sorted(root.rglob("*")):
        if count >= limit:
            break
        if not path.is_file():
            continue
        lowered_parts = {part.lower() for part in path.parts}
        if lowered_parts & SKIP_DIRS:
            continue
        if path.stat().st_size > 1_000_000:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name.lower() not in {"cookies", "login data", "local state"}:
            continue
        count += 1
        yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def lower_text(path: Path) -> str:
    return read_text(path).lower()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)
