from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .anonymize import stable_case_id, summarize_input
from .models import default_case_manifest, write_json
from .publish_check import publish_check_case
from .validation import validate_case


def create_public_case(
    input_path: Path,
    out: Path,
    *,
    case_id: str | None = None,
    source: str = "anonymized_user_case",
    framework: str = "generic",
    failure_type: str = "generic_automation_failure",
    subtype: str = "sanitized_failure_case",
) -> dict[str, Any]:
    input_path = Path(input_path)
    out = Path(out)
    case_id = case_id or stable_case_id(input_path, "public_case")
    if out.exists():
        shutil.rmtree(out)
    (out / "input").mkdir(parents=True)
    (out / "expected").mkdir()
    manifest = default_case_manifest(
        case_id,
        source=source,
        failure_type=failure_type,
        subtype=subtype,
        framework=framework,
    )
    write_json(out / "case_manifest.json", manifest)
    (out / "input" / "sanitized_input_summary.txt").write_text(
        summarize_input(input_path) + "\n", encoding="utf-8"
    )
    write_json(
        out / "expected" / "expected_diagnosis.json",
        {
            "failure_type": failure_type,
            "subtype": subtype,
            "framework": framework,
            "public_safe": True,
        },
    )
    (out / "README.md").write_text(
        f"# {case_id}\n\nSanitized public-safe failure case for Agent Failure Doctor.\n",
        encoding="utf-8",
    )
    (out / "LICENSE.md").write_text("MIT\n", encoding="utf-8")
    (out / "SAFETY.md").write_text(
        "This case is sanitized, local-only, diagnosis-only, and contains no credentials or non-public training materials.\n",
        encoding="utf-8",
    )
    validation = validate_case(out, out / "expected")
    publish = publish_check_case(out, out / "expected")
    return {"case_id": case_id, "case_dir": str(out), "validation": validation, "publish_check": publish}


def export_public_case(case_dir: Path, out: Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    out = Path(out)
    publish = publish_check_case(case_dir)
    if publish["status"] != "pass":
        raise ValueError("case did not pass publish-check")
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(case_dir, out)
    return {"status": "pass", "out": str(out), "case_id": publish.get("case_id")}
