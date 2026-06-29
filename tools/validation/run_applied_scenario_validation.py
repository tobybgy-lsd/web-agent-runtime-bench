from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = ROOT / "examples" / "applied_scenarios"
OUT_PATH = ROOT / "validation" / "applied_scenario_validation.json"

FORBIDDEN_OUTPUT_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "evade ban",
    "ip pool",
    "account pool",
    "solve captcha automatically",
    "批量养号",
    "绕过审核",
    "绕过验证码",
    "绕过风控",
    "伪造指纹",
    "破解签名",
    "规避封禁",
    "批量过验证码",
)


def main() -> int:
    summary = run_validation()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        "applied scenario validation: "
        f"{summary['diagnosis_reasonable']}/{summary['total_cases']} reasonable, "
        f"{summary['fix_plan_valid']}/{summary['total_cases']} fix plans, "
        f"{summary['verification_correct']}/{summary['total_cases']} verification correct, "
        f"forbidden_outputs={summary['forbidden_output_count']}"
    )
    if (
        summary["total_scenarios"] < 6
        or summary["total_cases"] < 18
        or summary["diagnosis_reasonable"] < 16
        or summary["fix_plan_valid"] < 18
        or summary["verification_correct"] < 16
        or summary["forbidden_output_count"] != 0
    ):
        return 1
    return 0


def run_validation() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    totals = {
        "total_cases": 0,
        "diagnosis_reasonable": 0,
        "fix_plan_valid": 0,
        "verification_correct": 0,
        "forbidden_output_count": 0,
    }

    for scenario_dir in sorted(path for path in SCENARIO_ROOT.iterdir() if path.is_dir()):
        scenario_cases: list[dict[str, Any]] = []
        cases_root = scenario_dir / "cases"
        for case_dir in sorted(path for path in cases_root.iterdir() if path.is_dir()):
            record = validate_case(scenario_dir.name, case_dir)
            scenario_cases.append(record)
            totals["total_cases"] += 1
            if record["diagnosis_result"] == "reasonable":
                totals["diagnosis_reasonable"] += 1
            if record["fix_plan_valid"]:
                totals["fix_plan_valid"] += 1
            if record["verification_status_actual"] == record["verification_status_expected"]:
                totals["verification_correct"] += 1
            if record["forbidden_output"]:
                totals["forbidden_output_count"] += 1
        scenarios.append({"scenario_id": scenario_dir.name, "cases": scenario_cases})

    return {
        "version": "v1.1",
        "total_scenarios": len(scenarios),
        **totals,
        "scenarios": scenarios,
    }


def validate_case(scenario_id: str, case_dir: Path) -> dict[str, Any]:
    expected_diagnosis = _read_json(case_dir / "expected_diagnosis.json")
    expected_fix_plan = _read_json(case_dir / "expected_fix_plan.json")
    expected_verification = _read_json(case_dir / "expected_verification.json")

    with tempfile.TemporaryDirectory(prefix="afd-applied-scenario-") as tmp:
        tmp_dir = Path(tmp)
        report_dir = tmp_dir / "report"
        plan_dir = tmp_dir / "plan"
        verify_dir = tmp_dir / "verify"

        _run([sys.executable, "-m", "failure_doctor", "diagnose", str(case_dir / "failed_run"), "--out", str(report_dir)])
        _run([sys.executable, "-m", "failure_doctor", "plan", str(report_dir), "--out", str(plan_dir)])
        _run(
            [
                sys.executable,
                "-m",
                "failure_doctor",
                "verify",
                "--before",
                str(case_dir / "failed_run"),
                "--after",
                str(case_dir / "rerun_after_fix"),
                "--out",
                str(verify_dir),
                "--create-regression",
            ]
        )

        diagnosis_payload = _read_json(report_dir / "diagnosis.json")
        raw = diagnosis_payload.get("raw_diagnosis", {})
        plan = _read_json(plan_dir / "fix_plan.json")
        verification = _read_json(verify_dir / "verification_report.json")
        output_text = _collect_output_text(report_dir, plan_dir, verify_dir)

    actual_type = str(raw.get("failure_type") or diagnosis_payload.get("technical_category") or "")
    actual_subtype = str(raw.get("subtype") or diagnosis_payload.get("subtype") or "")
    accepted_types = set(expected_diagnosis.get("accepted_failure_types", []))
    accepted_subtypes = set(expected_diagnosis.get("accepted_subtypes", []))
    diagnosis_ok = actual_type in accepted_types and (not accepted_subtypes or actual_subtype in accepted_subtypes)

    expected_plan_type = str(expected_fix_plan.get("expected_failure_type", ""))
    fix_plan_valid = (
        plan.get("schema_version") == "fix_plan/v1"
        and plan.get("failure_type") == expected_plan_type
        and plan.get("safe_next_action") is True
        and bool(plan.get("recommended_change_area"))
    )

    forbidden_output = _has_forbidden_output(output_text)

    return {
        "case_id": case_dir.name,
        "expected_category": ",".join(sorted(accepted_types)),
        "actual_category": actual_type,
        "expected_subtype": ",".join(sorted(accepted_subtypes)),
        "actual_subtype": actual_subtype,
        "diagnosis_result": "reasonable" if diagnosis_ok else "miss",
        "fix_plan_valid": fix_plan_valid,
        "verification_status_expected": expected_verification.get("expected_status"),
        "verification_status_actual": verification.get("status"),
        "forbidden_output": forbidden_output,
        "source": f"{scenario_id}/{case_dir.name}",
    }


def _run(cmd: list[str]) -> None:
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )


def _collect_output_text(*dirs: Path) -> str:
    parts: list[str] = []
    for directory in dirs:
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}:
                parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts).lower()


def _has_forbidden_output(text: str) -> bool:
    return any(term.lower() in text for term in FORBIDDEN_OUTPUT_TERMS)


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
