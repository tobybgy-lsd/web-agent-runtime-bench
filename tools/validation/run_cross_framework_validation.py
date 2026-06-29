from __future__ import annotations

import json
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, Mapping

from failure_doctor.cli import (
    diagnose_inputs,
    plan_from_report,
)
from integrations.cross_framework.common import normalize_framework_failure


FIXTURE_ROOT = Path("examples/cross_framework_fixtures")
OUTPUT_PATH = Path("validation/cross_framework_validation.json")
FORBIDDEN_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "account pool",
    "ip pool",
)


def run_validation() -> dict[str, Any]:
    cases = [_run_case(path) for path in _fixture_paths()]
    frameworks: dict[str, dict[str, int]] = {}
    for case in cases:
        bucket = frameworks.setdefault(case["framework"], {"cases": 0, "reasonable": 0})
        bucket["cases"] += 1
        if case["reasonable_category_match"]:
            bucket["reasonable"] += 1
    summary = {
        "version": "v2.2",
        "track": "cross_framework_adapter_validation",
        "total_cases": len(cases),
        "frameworks": frameworks,
        "overall": {
            "reasonable_category_match": sum(1 for case in cases if case["reasonable_category_match"]),
            "actionable_next_action": sum(1 for case in cases if case["actionable_next_action"]),
            "fix_plan_valid": sum(1 for case in cases if case["fix_plan_valid"]),
            "forbidden_output_count": sum(case["forbidden_output_count"] for case in cases),
            "severe_misclassification": sum(1 for case in cases if case["severe_misclassification"]),
        },
        "cases": cases,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    summary = run_validation()
    overall = summary["overall"]
    print("Cross-framework adapter validation")
    print(f"Cases: {summary['total_cases']}")
    print(f"Reasonable category match: {overall['reasonable_category_match']}")
    print(f"Actionable next action: {overall['actionable_next_action']}")
    print(f"Fix plan valid: {overall['fix_plan_valid']}")
    print(f"Forbidden output count: {overall['forbidden_output_count']}")
    print(f"Severe misclassification: {overall['severe_misclassification']}")
    ok = (
        summary["total_cases"] >= 40
        and overall["reasonable_category_match"] >= 35
        and overall["actionable_next_action"] == summary["total_cases"]
        and overall["fix_plan_valid"] == summary["total_cases"]
        and overall["forbidden_output_count"] == 0
        and overall["severe_misclassification"] <= 3
    )
    return 0 if ok else 1


def _fixture_paths() -> list[Path]:
    if not FIXTURE_ROOT.exists():
        return []
    return sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir() and (path / "raw").exists())


def _run_case(path: Path) -> dict[str, Any]:
    expected = _load_json(path / "expected_diagnosis.json")
    framework = str(expected.get("framework") or path.parent.name)
    if framework == "scrapy_requests":
        framework = _framework_from_case(path.name)
    with tempfile.TemporaryDirectory(prefix="afd_cross_framework_") as tmp:
        tmp_path = Path(tmp)
        pack_dir = tmp_path / "pack"
        report_dir = tmp_path / "report"
        plan_dir = tmp_path / "plan"
        metadata = normalize_framework_failure(path / "raw", framework, pack_dir)
        with redirect_stdout(StringIO()):
            diagnose_code = diagnose_inputs(_Args(input=str(pack_dir), out=str(report_dir), run_id=f"v22_{path.name}"))
            plan_code = plan_from_report(_Args(report=str(report_dir), out=str(plan_dir)))
        diagnosis = _load_json(report_dir / "diagnosis.json")
        plan = _load_json(plan_dir / "fix_plan.json")
        output_text = _collect_output_text(report_dir, plan_dir)

    actual_category = str(diagnosis.get("technical_category") or diagnosis.get("failure_type") or "unknown")
    actual_subtype = str(diagnosis.get("subtype") or "")
    expected_category = str(expected.get("technical_category"))
    accepted = set(expected.get("accepted_technical_categories", [expected_category]))
    reasonable = actual_category in accepted
    severe = actual_category not in accepted and actual_category not in {"insufficient_evidence", "unknown"}
    forbidden_count = sum(output_text.lower().count(term) for term in FORBIDDEN_TERMS)
    return {
        "case_id": path.name,
        "framework": framework,
        "expected_technical_category": expected_category,
        "expected_subtype": expected.get("subtype"),
        "actual_technical_category": actual_category,
        "actual_subtype": actual_subtype,
        "detected_error_family": metadata.get("detected_error_family"),
        "reasonable_category_match": reasonable,
        "actionable_next_action": bool(diagnosis.get("next_action")),
        "fix_plan_valid": plan_code == 0 and diagnose_code == 0 and bool(plan.get("fix_intent")),
        "forbidden_output_count": forbidden_count,
        "severe_misclassification": severe,
    }


def _framework_from_case(case_id: str) -> str:
    if case_id.startswith("requests_"):
        return "requests"
    if case_id.startswith("httpx_"):
        return "httpx"
    return "scrapy"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_output_text(*dirs: Path) -> str:
    parts: list[str] = []
    for directory in dirs:
        for file in directory.glob("*.md"):
            parts.append(file.read_text(encoding="utf-8", errors="replace"))
        for file in directory.glob("*.json"):
            parts.append(file.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


class _Args:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
