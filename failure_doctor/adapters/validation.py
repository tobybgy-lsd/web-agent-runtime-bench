from __future__ import annotations

from pathlib import Path

from .core import diagnose_adapter_input


def validate_adapter(kind: str, sample_input: Path, out_dir: Path) -> dict:
    result = diagnose_adapter_input(sample_input, out_dir, kind=kind)
    return {
        "status": "pass" if result.get("forbidden_output_count") == 0 else "fail",
        "adapter_kind": kind,
        "subtype": result.get("subtype"),
    }
