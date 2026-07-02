from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CASE_SCHEMA_VERSION = "public_case/v1"
ISSUE_PACK_SCHEMA_VERSION = "issue_pack/v1"
SAFE_LICENSES = {"MIT", "CC-BY-4.0", "project-compatible"}
REQUIRED_CASE_FILES = ("case_manifest.json", "README.md", "LICENSE.md", "SAFETY.md")
REQUIRED_CASE_DIRS = ("input", "expected")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_case_manifest(
    case_id: str,
    *,
    source: str = "synthetic",
    failure_type: str = "generic_automation_failure",
    subtype: str = "generic_public_safe_case",
    framework: str = "generic",
) -> dict[str, Any]:
    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_id": case_id,
        "created_at": utc_now(),
        "source": source,
        "public_safe": True,
        "sanitized": True,
        "contains_real_secret": False,
        "contains_private_solution": False,
        "contains_customer_data": False,
        "contains_pii": False,
        "contains_phi": False,
        "contains_credentials": False,
        "diagnosis_only_no_bypass": True,
        "license": "MIT",
        "failure_type": failure_type,
        "subtype": subtype,
        "framework": framework,
        "expected_outputs": ["diagnosis", "safety", "full_chain", "benchmark_score"],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
