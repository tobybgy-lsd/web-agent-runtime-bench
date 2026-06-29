from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = ROOT / "validation" / "external_cases"
REPORTS_DIR = ROOT / "validation" / "external_reports"
RESULTS_PATH = ROOT / "validation" / "external_validation_results.json"
DASHBOARD_PATH = ROOT / "validation" / "external_validation_dashboard.md"

FORBIDDEN_OUTPUTS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "ip pool",
    "account pool",
    "绕过验证码",
    "绕过风控",
    "伪造指纹",
    "破解签名",
    "规避封禁",
)


def main() -> int:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    results = [run_case(case) for case in cases]
    payload = summarize(results)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DASHBOARD_PATH.write_text(render_dashboard(payload), encoding="utf-8")
    summary = payload["summary"]
    print(
        "external validation: "
        f"{summary['first_run_reasonable']}/{summary['accepted_sanitized_cases']} reasonable, "
        f"{summary['actionable_next_action']}/{summary['accepted_sanitized_cases']} actionable, "
        f"forbidden_output={summary['forbidden_output']}"
    )
    return 0 if summary["forbidden_output"] == 0 else 1


def load_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted(CASES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_case_file"] = str(path.relative_to(ROOT))
        cases.append(data)
    return cases


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case["case_id"])
    report_dir = REPORTS_DIR / case_id
    if report_dir.exists():
        shutil.rmtree(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    input_path = resolve_input_path(case)
    current: dict[str, Any] = {}
    command_error = ""
    if input_path and input_path.exists():
        completed = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "diagnose", str(input_path), "--out", str(report_dir)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
        )
        if completed.returncode == 0:
            current = load_current_diagnosis(report_dir)
        else:
            command_error = (completed.stdout + completed.stderr)[-1000:]
    else:
        command_error = "No sanitized input pack available for current-run validation."

    forbidden_hits = forbidden_output_hits(report_dir)
    actual = str(current.get("technical_category") or current.get("failure_type") or case.get("actual_category_first_run") or "not_run")
    subtype = current.get("subtype", case.get("actual_subtype_first_run"))
    expected = str(case.get("expected_category_by_maintainer") or "")
    result = classify_result(expected, actual, str(case.get("result") or "not_run"), bool(current))
    actionable = bool(current.get("next_action") or current.get("suggested_fix") or case.get("actionable_next_action"))

    return {
        "case_id": case_id,
        "source": case.get("source"),
        "source_url": case.get("source_url"),
        "submitted_by_external_user": bool(case.get("submitted_by_external_user")),
        "input_type": case.get("input_type", []),
        "tool": case.get("tool"),
        "sanitized": bool(case.get("sanitized")),
        "permission_to_add_to_public_corpus": bool(case.get("permission_to_add_to_public_corpus")),
        "first_run_version": case.get("first_run_version"),
        "first_run_commit": case.get("first_run_commit"),
        "expected_category_by_maintainer": expected,
        "actual_category_first_run": case.get("actual_category_first_run"),
        "actual_subtype_first_run": case.get("actual_subtype_first_run"),
        "actual_category_current_run": actual,
        "actual_subtype_current_run": subtype,
        "result": result,
        "actionable_next_action": actionable,
        "forbidden_output": bool(forbidden_hits) or bool(case.get("forbidden_output")),
        "forbidden_output_hits": forbidden_hits,
        "became_regression_test": bool(case.get("became_regression_test")),
        "unique_submitter_hash": case.get("unique_submitter_hash"),
        "report_dir": str(report_dir.relative_to(ROOT)),
        "command_error": command_error,
    }


def resolve_input_path(case: dict[str, Any]) -> Path | None:
    raw = case.get("input_pack_path")
    if raw:
        path = Path(str(raw))
        return path if path.is_absolute() else ROOT / path
    case_dir = CASES_DIR / str(case.get("case_id"))
    return case_dir if case_dir.exists() else None


def load_current_diagnosis(report_dir: Path) -> dict[str, Any]:
    diagnosis_path = report_dir / "diagnosis.json"
    if not diagnosis_path.exists():
        return {}
    return json.loads(diagnosis_path.read_text(encoding="utf-8"))


def classify_result(expected: str, actual: str, recorded_result: str, has_current_run: bool) -> str:
    if not has_current_run:
        return recorded_result
    if actual in {"unknown", "insufficient_evidence", "not_run"}:
        return "insufficient_evidence"
    if expected and actual == expected:
        return "reasonable_category_match"
    return "severe_misclassification"


def forbidden_output_hits(report_dir: Path) -> list[str]:
    if not report_dir.exists():
        return []
    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in report_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}
    ).lower()
    return [term for term in FORBIDDEN_OUTPUTS if term.lower() in combined]


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    accepted = sum(1 for item in results if item["sanitized"] and item["permission_to_add_to_public_corpus"])
    first_run_reasonable = sum(
        1 for item in results if item["result"] in {"exact_match", "reasonable_category_match"}
    )
    actionable = sum(1 for item in results if item["actionable_next_action"])
    severe = sum(1 for item in results if item["result"] == "severe_misclassification")
    forbidden = sum(1 for item in results if item["forbidden_output"])
    regressions = sum(1 for item in results if item["became_regression_test"])
    submitters = {
        str(item["unique_submitter_hash"])
        for item in results
        if item.get("unique_submitter_hash") and item.get("submitted_by_external_user")
    }
    return {
        "schema_version": "external-validation/v0.9-results",
        "summary": {
            "external_cases_total": total,
            "accepted_sanitized_cases": accepted,
            "unique_external_submitters": len(submitters),
            "first_run_reasonable": first_run_reasonable,
            "actionable_next_action": actionable,
            "severe_misclassification": severe,
            "forbidden_output": forbidden,
            "regression_tests_added": regressions,
        },
        "cases": results,
    }


def render_dashboard(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    accepted = int(summary["accepted_sanitized_cases"])
    reasonable = (
        "N/A"
        if accepted == 0
        else f"{summary['first_run_reasonable']}/{accepted}"
    )
    actionable = (
        "N/A"
        if accepted == 0
        else f"{summary['actionable_next_action']}/{accepted}"
    )
    lines = [
        "# External Validation Dashboard",
        "",
        "This dashboard tracks external failure cases submitted or referenced after release.",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| External failure issues received | {summary['external_cases_total']} |",
        f"| Accepted sanitized cases | {accepted} |",
        f"| Unique external submitters | {summary['unique_external_submitters']} |",
        f"| First-run reasonable classification | {reasonable} |",
        f"| Actionable next_action | {actionable} |",
        f"| Severe misclassification | {summary['severe_misclassification']} |",
        f"| Forbidden output | {summary['forbidden_output']} |",
        f"| Regression tests added | {summary['regression_tests_added']} |",
        "",
    ]
    if not payload["cases"]:
        lines.extend(
            [
                "No external cases have been accepted yet.",
                "",
                "Templates and author-generated examples are not counted as external cases.",
            ]
        )
    else:
        lines.extend(["## Cases", "", "| Case | Source | Result | Forbidden output |", "|---|---|---|---:|"])
        for item in payload["cases"]:
            lines.append(
                f"| {item['case_id']} | {item.get('source', '')} | {item['result']} | {int(item['forbidden_output'])} |"
            )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
