from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


@dataclass
class RedactionReport:
    categories: dict[str, int] = field(default_factory=dict)

    def add(self, category: str, count: int) -> None:
        if count:
            self.categories[category] = self.categories.get(category, 0) + count

    @property
    def total_redactions(self) -> int:
        return sum(self.categories.values())

    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": "failure-doctor-redaction-report/v2.1",
            "total_redactions": self.total_redactions,
            "categories": self.categories,
        }


TEXT_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (
        "authorization",
        r"(?i)\bAuthorization\s*[:=]\s*Bearer\s+[A-Za-z0-9._~+/=-]+",
        "Authorization: [REDACTED_AUTHORIZATION]",
    ),
    (
        "authorization",
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+",
        "[REDACTED_AUTHORIZATION]",
    ),
    (
        "cookie",
        r"(?i)\bCookie\s*[:=]\s*[^\r\n]+",
        "Cookie: [REDACTED_COOKIE]",
    ),
    (
        "api_key",
        r"(?i)\b(api[_-]?key|x-api-key)\s*[:=]\s*sk-[A-Za-z0-9._-]+",
        r"\1=[REDACTED_API_KEY]",
    ),
    ("api_key", r"\bsk-[A-Za-z0-9]{12,}\b", "[REDACTED_API_KEY]"),
    (
        "internal_url",
        r"https?://[^\s\"'<>()]*(?:internal|company|corp|intranet|localhost|\.local)[^\s\"'<>()]*",
        "[REDACTED_INTERNAL_URL]",
    ),
    (
        "internal_url",
        r"https?://[^\s\"'<>()]*(?:/internal/)[^\s\"'<>()]*",
        "[REDACTED_INTERNAL_URL]",
    ),
    (
        "email",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
    ),
    ("phone", r"(?<!\d)1[3-9]\d{9}(?!\d)", "[REDACTED_PHONE]"),
    ("id_card", r"(?<!\d)\d{17}[\dXx](?!\d)", "[REDACTED_ID]"),
    ("order_id", r"\bORD-\d{8}-\d+\b", "[REDACTED_ORDER_ID]"),
    (
        "customer_name",
        r"(?i)\b(customer|customer_name|client|buyer|客户|客户名)\s*[:= ]+\s*[\w\u4e00-\u9fff-]+",
        r"\1 [REDACTED_CUSTOMER_NAME]",
    ),
)

SENSITIVE_JSON_KEYS = {
    "authorization": "[REDACTED_AUTHORIZATION]",
    "cookie": "[REDACTED_COOKIE]",
    "set-cookie": "[REDACTED_COOKIE]",
    "x-api-key": "[REDACTED_API_KEY]",
    "api_key": "[REDACTED_API_KEY]",
    "apikey": "[REDACTED_API_KEY]",
    "token": "[REDACTED_SECRET]",
    "password": "[REDACTED_SECRET]",
    "secret": "[REDACTED_SECRET]",
}


def sanitize_failure_pack(input_path: Path, out_dir: Path) -> dict[str, Any]:
    input_path = input_path.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"input not found: {input_path}")
    out_dir = out_dir.resolve()
    _guard_output_path(input_path, out_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = RedactionReport()
    source_files = _source_files(input_path)

    log_text = _combined_log_text(source_files)
    sanitized_log = redact_text(log_text, report) if log_text else ""
    (out_dir / "sanitized_error.log").write_text(sanitized_log, encoding="utf-8")

    network_payload = _combined_network_payload(source_files)
    sanitized_network = sanitize_json(network_payload, report)
    (out_dir / "sanitized_network.json").write_text(
        json.dumps(sanitized_network, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    trace_metadata = trace_metadata_for(source_files)
    (out_dir / "sanitized_trace_metadata.json").write_text(
        json.dumps(trace_metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    redaction_payload = report.payload()
    (out_dir / "redaction_report.json").write_text(
        json.dumps(redaction_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    safe_payload = safe_to_share_payload(redaction_payload, trace_metadata)
    (out_dir / "safe_to_share.json").write_text(
        json.dumps(safe_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    (out_dir / "README_FOR_REVIEWER.md").write_text(
        reviewer_readme(input_path, redaction_payload, safe_payload),
        encoding="utf-8",
    )
    zip_path = write_shareable_zip(out_dir)
    return {
        "out_dir": str(out_dir),
        "zip_path": str(zip_path),
        "redaction_report": redaction_payload,
        "safe_to_share": safe_payload,
        "trace_metadata": trace_metadata,
    }


def redact_text(text: str, report: RedactionReport) -> str:
    redacted = text
    for category, pattern, replacement in TEXT_PATTERNS:
        redacted, count = re.subn(pattern, replacement, redacted)
        report.add(category, count)
    return redacted


def sanitize_json(value: Any, report: RedactionReport) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_lower = str(key).lower()
            if key_lower in SENSITIVE_JSON_KEYS:
                placeholder = SENSITIVE_JSON_KEYS[key_lower]
                category = _category_for_placeholder(placeholder)
                report.add(category, 1)
                sanitized[key] = placeholder
            else:
                sanitized[key] = sanitize_json(item, report)
        return sanitized
    if isinstance(value, list):
        return [sanitize_json(item, report) for item in value]
    if isinstance(value, str):
        return redact_text(value, report)
    return value


def trace_metadata_for(files: list[Path]) -> dict[str, Any]:
    archives = []
    for path in files:
        if path.name.lower().endswith(".zip") and "trace" in path.name.lower():
            archives.append(
                {
                    "filename": path.name,
                    "size_bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                    "raw_trace_included": False,
                    "note": "Raw trace archive is intentionally not copied into the shareable pack.",
                }
            )
    return {
        "schema_version": "sanitized-trace-metadata/v2.1",
        "trace_archives": archives,
    }


def safe_to_share_payload(
    redaction_report: dict[str, Any],
    trace_metadata: dict[str, Any],
) -> dict[str, Any]:
    review = [
        "Manual review required before posting or sending this pack.",
        "Confirm screenshots, trace attachments, private URLs, customer data, and credentials are absent.",
    ]
    if redaction_report.get("total_redactions", 0):
        review.append("Redactions were applied; inspect placeholders and surrounding text.")
    if trace_metadata.get("trace_archives"):
        review.append("Raw trace.zip was not included; attach it only after separate sanitization.")
    return {
        "schema_version": "safe-to-share/v2.1",
        "safe_to_share": False,
        "required_review": review,
        "redaction_replacement_count": redaction_report.get("total_redactions", 0),
        "policy": "local sanitized evidence only; no credentials or private customer data",
    }


def reviewer_readme(
    input_path: Path,
    redaction_report: dict[str, Any],
    safe_payload: dict[str, Any],
) -> str:
    categories = ", ".join(sorted(redaction_report.get("categories", {}).keys())) or "none"
    return "\n".join(
        [
            "# Sanitized Failure Pack",
            "",
            "This pack was generated locally by Agent Failure Doctor v2.1.",
            "",
            f"- Source folder/file: `{input_path.name}`",
            f"- Redaction count: `{redaction_report.get('total_redactions', 0)}`",
            f"- Redaction categories: `{categories}`",
            f"- Safe to share automatically: `{safe_payload.get('safe_to_share')}`",
            "",
            "## Files",
            "",
            "- `sanitized_error.log`: redacted text logs.",
            "- `sanitized_network.json`: redacted network summary, if provided.",
            "- `sanitized_trace_metadata.json`: trace archive metadata only; raw trace.zip is not copied.",
            "- `redaction_report.json`: redaction categories and counts.",
            "- `safe_to_share.json`: conservative review gate.",
            "",
            "Review this folder manually before attaching it to a public issue.",
            "",
        ]
    )


def write_shareable_zip(out_dir: Path) -> Path:
    zip_path = out_dir / "shareable_failure_pack.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(out_dir.iterdir()):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.name)
    return zip_path


def _source_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(item for item in path.iterdir() if item.is_file())


def _guard_output_path(input_path: Path, out_dir: Path) -> None:
    if out_dir == input_path:
        raise ValueError("sanitize --out must not be the input path")
    if input_path.is_dir() and input_path in out_dir.parents:
        raise ValueError("sanitize --out must not be inside the input path")


def _combined_log_text(files: list[Path]) -> str:
    chunks: list[str] = []
    for path in files:
        lower = path.name.lower()
        if lower.endswith((".log", ".txt")) and "network" not in lower:
            chunks.append(f"===== {path.name} =====\n{path.read_text(encoding='utf-8', errors='replace')}")
    return "\n\n".join(chunks)


def _combined_network_payload(files: list[Path]) -> list[Any]:
    events: list[Any] = []
    for path in files:
        lower = path.name.lower()
        if lower.endswith(".json") and "network" in lower:
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                events.append({"filename": path.name, "parse_error": "invalid_json"})
                continue
            if isinstance(parsed, list):
                events.extend(parsed)
            else:
                events.append(parsed)
    return events


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _category_for_placeholder(placeholder: str) -> str:
    if "AUTHORIZATION" in placeholder:
        return "authorization"
    if "COOKIE" in placeholder:
        return "cookie"
    if "API_KEY" in placeholder:
        return "api_key"
    return "secret"
