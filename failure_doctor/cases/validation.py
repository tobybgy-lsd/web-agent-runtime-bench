from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import CASE_SCHEMA_VERSION, REQUIRED_CASE_DIRS, REQUIRED_CASE_FILES, read_json, write_json
from .publish_check import publish_check_case


def validate_case(case_dir: Path, out: Path | None = None) -> dict[str, Any]:
    case_dir = Path(case_dir)
    missing = [name for name in REQUIRED_CASE_FILES if not (case_dir / name).exists()]
    missing += [name for name in REQUIRED_CASE_DIRS if not (case_dir / name).is_dir()]
    manifest = read_json(case_dir / "case_manifest.json") if (case_dir / "case_manifest.json").exists() else {}
    schema_valid = manifest.get("schema_version") == CASE_SCHEMA_VERSION
    publish = publish_check_case(case_dir)
    payload = {
        "schema_version": "case_validation/v1",
        "case_id": manifest.get("case_id"),
        "status": "pass" if not missing and schema_valid and publish["status"] == "pass" else "fail",
        "missing": missing,
        "schema_valid": schema_valid,
        "publish_check_status": publish["status"],
        "public_safe": publish["public_safe"],
    }
    if out is not None:
        write_json(Path(out) / "case_validation.json", payload)
    return payload
