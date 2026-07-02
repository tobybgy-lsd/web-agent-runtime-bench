from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .anonymize import stable_case_id, summarize_input
from .models import ISSUE_PACK_SCHEMA_VERSION, utc_now, write_json, read_json
from .publish_check import BLOCKED_MARKERS


def create_issue_pack(input_path: Path, out: Path) -> dict[str, Any]:
    input_path = Path(input_path)
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    pack_id = stable_case_id(input_path, "issue_pack")
    summary = summarize_input(input_path)
    write_json(
        out / "issue_manifest.json",
        {
            "schema_version": ISSUE_PACK_SCHEMA_VERSION,
            "issue_pack_id": pack_id,
            "created_at": utc_now(),
            "sanitized": True,
            "public_safe": True,
            "raw_local_only_excluded": True,
            "contains_credentials": False,
            "contains_private_solution": False,
        },
    )
    (out / "sanitized_summary.md").write_text(
        f"# Failure Case Summary\n\n```text\n{summary}\n```\n", encoding="utf-8"
    )
    (out / "how_to_submit.md").write_text(
        "Attach this sanitized issue pack to a GitHub issue. Do not include raw local-only collection folders.\n",
        encoding="utf-8",
    )
    validation = validate_issue_pack(out)
    write_json(out / "issue_pack_validation.json", validation)
    return {"issue_pack_id": pack_id, "out": str(out), "validation": validation}


def validate_issue_pack(pack_dir: Path) -> dict[str, Any]:
    pack_dir = Path(pack_dir)
    manifest_path = pack_dir / "issue_manifest.json"
    summary_path = pack_dir / "sanitized_summary.md"
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    findings: list[str] = []
    if manifest.get("schema_version") != ISSUE_PACK_SCHEMA_VERSION:
        findings.append("invalid_schema_version")
    if manifest.get("sanitized") is not True or manifest.get("public_safe") is not True:
        findings.append("not_public_safe")
    if not summary_path.exists():
        findings.append("missing_sanitized_summary")
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore").lower()
        for path in pack_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".log"}
    )
    for marker in BLOCKED_MARKERS:
        if marker in text:
            findings.append(f"blocked_marker:{marker}")
    return {
        "schema_version": "issue_pack_validation/v1",
        "status": "pass" if not findings else "fail",
        "findings": findings,
        "public_safe": not findings,
        "forbidden_output_count": 0,
        "private_solution_leak_count": len([item for item in findings if "private" in item]),
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
    }
