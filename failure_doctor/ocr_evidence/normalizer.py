from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import SCHEMA_VERSION, TOOL_VERSION


def normalize_ocr_payload(input_path: Path, provider: str, provider_mode: str, raw: dict[str, Any], safety: dict[str, Any]) -> dict[str, Any]:
    text_blocks = _blocks(raw.get("text_blocks", []))
    tables = _tables(raw.get("tables", []))
    forms = _forms(raw.get("forms", []))
    layout = list(raw.get("layout", []))
    warnings = list(raw.get("warnings", []))
    if raw.get("provider_unavailable"):
        warnings.append("provider_unavailable")
    if raw.get("cloud_blocked"):
        warnings.append("ocr_cloud_upload_blocked")
    return {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "provider_mode": provider_mode,
        "input": {
            "path": str(input_path),
            "kind": _guess_kind(input_path),
            "sha256": _sha256(input_path),
            "size_bytes": _size(input_path),
        },
        "safety": safety,
        "text_blocks": text_blocks,
        "tables": tables,
        "forms": forms,
        "layout": layout,
        "warnings": sorted(set(warnings)),
        "confidence_summary": _confidence(raw, text_blocks, tables, forms),
    }


def _blocks(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for idx, item in enumerate(values, start=1):
        blocks.append(
            {
                "id": str(item.get("id") or f"text_{idx:03d}"),
                "text": str(item.get("text", "")),
                "bbox": item.get("bbox", [0, 0, 0, 0]),
                "confidence": float(item.get("confidence", 0.0)),
                "language": item.get("language", "unknown"),
                "source_page": int(item.get("source_page", 1)),
                "reading_order": int(item.get("reading_order", idx)),
                "redacted": bool(item.get("redacted", False)),
            }
        )
    return blocks


def _tables(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    for idx, item in enumerate(values, start=1):
        cells = item.get("cells", [])
        rows = int(item.get("rows", len(cells) or 0))
        columns = int(item.get("columns", max((len(row) for row in cells), default=0) if isinstance(cells, list) else 0))
        tables.append(
            {
                "id": str(item.get("id") or f"table_{idx:03d}"),
                "bbox": item.get("bbox", [0, 0, 0, 0]),
                "rows": rows,
                "columns": columns,
                "cells": cells,
                "confidence": float(item.get("confidence", 0.0)),
                "warnings": list(item.get("warnings", [])),
            }
        )
    return tables


def _forms(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    forms: list[dict[str, Any]] = []
    for idx, item in enumerate(values, start=1):
        forms.append({"id": str(item.get("id") or f"form_{idx:03d}"), "fields": list(item.get("fields", []))})
    return forms


def _confidence(raw: dict[str, Any], blocks: list[dict[str, Any]], tables: list[dict[str, Any]], forms: list[dict[str, Any]]) -> dict[str, float]:
    if isinstance(raw.get("confidence_summary"), dict):
        base = raw["confidence_summary"]
        return {
            "overall": float(base.get("overall", 0.0)),
            "text": float(base.get("text", 0.0)),
            "table": float(base.get("table", 0.0)),
            "form": float(base.get("form", 0.0)),
        }
    values = [float(b.get("confidence", 0.0)) for b in blocks]
    table_values = [float(t.get("confidence", 0.0)) for t in tables]
    form_values = [float(fld.get("confidence", 0.0)) for form in forms for fld in form.get("fields", [])]
    all_values = values + table_values + form_values
    avg = sum(all_values) / len(all_values) if all_values else 0.0
    return {
        "overall": round(avg, 3),
        "text": round(sum(values) / len(values), 3) if values else 0.0,
        "table": round(sum(table_values) / len(table_values), 3) if table_values else 0.0,
        "form": round(sum(form_values) / len(form_values), 3) if form_values else 0.0,
    }


def _guess_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if path.is_dir():
        return "mixed"
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".png", ".jpg", ".jpeg"}:
        return "screenshot"
    return "mixed"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    for file_path in files:
        h.update(file_path.name.encode("utf-8", errors="replace"))
        try:
            h.update(file_path.read_bytes())
        except OSError:
            continue
    return h.hexdigest()


def _size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
