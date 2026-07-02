from __future__ import annotations

import hashlib
import re
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[A-Za-z0-9._\-]+"),
    re.compile(r"(?i)(token\s*[:=]\s*)[A-Za-z0-9._\-]+"),
    re.compile(r"(?i)(password\s*[:=]\s*)[^\s]+"),
    re.compile(r"(?i)(cookie:\s*)[^\n\r]+"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
)

PATH_PATTERNS = (
    re.compile(r"[A-Z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
)


def stable_case_id(input_path: Path, prefix: str = "case") -> str:
    digest = hashlib.sha256(str(input_path.resolve()).encode("utf-8", errors="ignore")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def anonymize_text(text: str) -> str:
    value = text
    for pattern in SECRET_PATTERNS:
        value = pattern.sub(lambda match: (match.group(1) if match.groups() else "") + "<REDACTED>", value)
    for pattern in PATH_PATTERNS:
        value = pattern.sub("<LOCAL_PATH>", value)
    return value


def summarize_input(input_path: Path, limit: int = 12_000) -> str:
    input_path = Path(input_path)
    if input_path.is_file():
        return _read_public_safe_text(input_path, limit)
    chunks: list[str] = []
    for path in sorted(input_path.rglob("*")):
        if not path.is_file() or path.stat().st_size > 512_000:
            continue
        if path.suffix.lower() not in {".txt", ".log", ".json", ".md", ".xml", ".yaml", ".yml", ".html"}:
            continue
        rel = path.relative_to(input_path)
        chunks.append(f"--- {rel} ---\n{_read_public_safe_text(path, 2000)}")
        if sum(len(chunk) for chunk in chunks) >= limit:
            break
    return anonymize_text("\n\n".join(chunks))[:limit]


def _read_public_safe_text(path: Path, limit: int) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        text = ""
    return anonymize_text(text[:limit])
