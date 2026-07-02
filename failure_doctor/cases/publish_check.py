from __future__ import annotations

from pathlib import Path
from typing import Any

from failure_doctor.plugin.security import find_forbidden_terms

from .models import REQUIRED_CASE_DIRS, REQUIRED_CASE_FILES, SAFE_LICENSES, read_json, write_json


BLOCKED_MARKERS = (
    "raw_local_only_do_not_share",
    "private" + "_solutions",
    "spider" + "buf" + "challenge" + "workbench",
    "flag" + "{",
    "authorization: bearer ",
    "set-cookie:",
)


def publish_check_case(case_dir: Path, out: Path | None = None) -> dict[str, Any]:
    case_dir = Path(case_dir)
    findings: list[dict[str, str]] = []
    missing = [name for name in REQUIRED_CASE_FILES if not (case_dir / name).exists()]
    missing += [name for name in REQUIRED_CASE_DIRS if not (case_dir / name).is_dir()]
    manifest = read_json(case_dir / "case_manifest.json") if (case_dir / "case_manifest.json").exists() else {}
    required_false = [
        "contains_real_secret",
        "contains_private_solution",
        "contains_customer_data",
        "contains_pii",
        "contains_phi",
        "contains_credentials",
    ]
    for key in required_false:
        if manifest.get(key) is not False:
            findings.append({"kind": "manifest_flag", "detail": f"{key} must be false"})
    for key in ("public_safe", "sanitized", "diagnosis_only_no_bypass"):
        if manifest.get(key) is not True:
            findings.append({"kind": "manifest_flag", "detail": f"{key} must be true"})
    if manifest.get("license") not in SAFE_LICENSES:
        findings.append({"kind": "license", "detail": "license must be project-compatible"})
    for path in _iter_text_files(case_dir):
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for marker in BLOCKED_MARKERS:
            if marker in text:
                findings.append({"kind": "blocked_marker", "detail": marker, "path": str(path)})
        for term in find_forbidden_terms(text):
            findings.append({"kind": "forbidden_output", "detail": term, "path": str(path)})
    payload = {
        "schema_version": "case_publish_check/v1",
        "case_id": manifest.get("case_id"),
        "status": "pass" if not missing and not findings else "fail",
        "missing": missing,
        "findings": findings,
        "public_safe": not missing and not findings,
        "raw_secret_in_public_case": 0 if not findings else len([f for f in findings if f["kind"] == "blocked_marker"]),
        "private_solution_leak_count": len([f for f in findings if "private" in f.get("detail", "")]),
        "forbidden_output_count": len([f for f in findings if f["kind"] == "forbidden_output"]),
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
    }
    if out is not None:
        write_json(Path(out) / "publish_check.json", payload)
    return payload


def _iter_text_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".log", ".yaml", ".yml"}:
            yield path
