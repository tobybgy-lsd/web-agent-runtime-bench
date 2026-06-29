from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from failure_doctor.cli import failure_layer_for


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "examples" / "realistic_playwright_traces"
OUT_PATH = ROOT / "validation" / "real_trace_validation_30.json"
TMP_ROOT = ROOT / "tmp" / "real_trace_validation"

FORBIDDEN_OUTPUT_TERMS = (
    "captcha bypass",
    "bot evasion",
    "spoof fingerprint",
    "fingerprint spoofing",
    "crack signature",
    "dynamic signature cracking",
    "bypass cloudflare",
    "evade ban",
    "ip pool",
    "account pool",
    "solve captcha automatically",
)


def main() -> int:
    cases = sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir())
    if TMP_ROOT.exists():
        shutil.rmtree(TMP_ROOT)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)

    results = []
    for case_dir in cases:
        result = validate_case(case_dir)
        results.append(result)

    summary = summarize(results)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "real trace validation: "
        f"{summary['reasonable_category_match']}/{summary['total_cases']} reasonable, "
        f"{summary['exact_subtype_match']}/{summary['total_cases']} exact, "
        f"forbidden_outputs={summary['forbidden_output_count']}"
    )
    return 0


def validate_case(case_dir: Path) -> dict[str, Any]:
    expected = json.loads((case_dir / "expected_diagnosis.json").read_text(encoding="utf-8"))
    out_dir = TMP_ROOT / case_dir.name
    trace_zip = case_dir / "trace.zip"
    if trace_zip.exists():
        cmd = [sys.executable, "-m", "trace_doctor", "diagnose", str(trace_zip), "--out", str(out_dir)]
        input_type = "native_playwright_trace_zip"
    else:
        input_path = case_dir / "optional_input_pack" if (case_dir / "optional_input_pack").exists() else case_dir
        cmd = [sys.executable, "-m", "failure_doctor", "diagnose", str(input_path), "--out", str(out_dir)]
        input_type = "failure_input_pack"

    completed = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        return {
            "case_id": case_dir.name,
            "input_type": input_type,
            "expected": expected,
            "actual": {},
            "result": "insufficient_evidence",
            "notes": (completed.stdout + completed.stderr)[-500:],
        }

    diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
    actual_technical = str(diagnosis.get("technical_category") or diagnosis.get("failure_type") or "unknown")
    actual_subtype = diagnosis.get("subtype")
    actual = {
        "failure_layer": str(diagnosis.get("failure_layer") or failure_layer_for(actual_technical)),
        "technical_category": actual_technical,
        "subtype": actual_subtype,
        "evidence_level": diagnosis.get("evidence_level", "inferred"),
        "safe_next_action": bool(diagnosis.get("safe_next_action", True)),
    }
    result = classify_result(expected, actual)
    forbidden = forbidden_output_count(out_dir)
    return {
        "case_id": case_dir.name,
        "input_type": input_type,
        "expected": expected,
        "actual": actual,
        "result": result,
        "forbidden_output_count": forbidden,
        "actionable_next_action": bool(diagnosis.get("suggested_fix") or diagnosis.get("next_action")),
        "notes": "",
    }


def classify_result(expected: dict[str, Any], actual: dict[str, Any]) -> str:
    if actual.get("technical_category") in {"unknown", "insufficient_evidence"}:
        return "insufficient_evidence"
    if (
        actual.get("technical_category") == expected.get("technical_category")
        and actual.get("subtype") == expected.get("subtype")
    ):
        return "exact_match"
    if actual.get("technical_category") == expected.get("technical_category"):
        return "category_match"
    if actual.get("failure_layer") == expected.get("failure_layer"):
        return "category_match"
    return "severe_misclassification"


def forbidden_output_count(out_dir: Path) -> int:
    count = 0
    for path in out_dir.glob("*"):
        if path.suffix.lower() not in {".md", ".json", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        count += sum(1 for term in FORBIDDEN_OUTPUT_TERMS if term in text)
    return count


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    exact = sum(1 for item in results if item["result"] == "exact_match")
    reasonable = sum(1 for item in results if item["result"] in {"exact_match", "category_match"})
    insufficient = sum(1 for item in results if item["result"] == "insufficient_evidence")
    severe = sum(1 for item in results if item["result"] == "severe_misclassification")
    actionable = sum(1 for item in results if item.get("actionable_next_action"))
    forbidden = sum(int(item.get("forbidden_output_count", 0)) for item in results)
    return {
        "version": "v0.8",
        "track": "real_playwright_trace_semantic_validation",
        "total_cases": total,
        "exact_subtype_match": exact,
        "reasonable_category_match": reasonable,
        "actionable_next_action": actionable,
        "insufficient_evidence": insufficient,
        "severe_misclassification": severe,
        "forbidden_output_count": forbidden,
        "cases": results,
    }


if __name__ == "__main__":
    raise SystemExit(main())

