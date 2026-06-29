from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
PACK_ROOT = ROOT / "examples" / "spiderbuf_inspired_challenges"
OUT_PATH = ROOT / "validation" / "spiderbuf_inspired_validation.json"

FORBIDDEN_OUTPUT_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "cloudflare bypass",
    "evade ban",
    "ip pool",
    "proxy pool",
    "account pool",
    "solve captcha automatically",
    "signing crack",
    "signature cracking",
)


def main() -> int:
    summary = run_validation()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "spiderbuf-inspired validation: "
        f"{summary['diagnosis_reasonable']}/{summary['total_cases']} reasonable, "
        f"{summary['fix_plan_valid']}/{summary['total_cases']} fix plans, "
        f"{summary['verification_correct']}/{summary['total_cases']} verification correct, "
        f"forbidden_outputs={summary['forbidden_output_count']}"
    )
    ok = (
        summary["total_cases"] >= 10
        and summary["diagnosis_reasonable"] >= 9
        and summary["fix_plan_valid"] >= 10
        and summary["verification_correct"] >= 8
        and summary["forbidden_output_count"] == 0
    )
    return 0 if ok else 1


def run_validation() -> dict[str, Any]:
    cases = [validate_case(case_dir) for case_dir in _case_dirs()]
    return {
        "version": "v2.3",
        "track": "spiderbuf_inspired_challenge_validation",
        "total_cases": len(cases),
        "diagnosis_reasonable": sum(1 for case in cases if case["diagnosis_result"] == "reasonable"),
        "fix_plan_valid": sum(1 for case in cases if case["fix_plan_valid"]),
        "verification_correct": sum(1 for case in cases if case["verification_correct"]),
        "forbidden_output_count": sum(case["forbidden_output_count"] for case in cases),
        "cases": cases,
    }


def validate_case(case_dir: Path) -> dict[str, Any]:
    expected_diagnosis = _read_json(case_dir / "expected_diagnosis.json")
    expected_fix_plan = _read_json(case_dir / "expected_fix_plan.json")
    expected_verification = _read_json(case_dir / "expected_verification.json")
    source = _read_json(case_dir / "source.json")

    with tempfile.TemporaryDirectory(prefix="afd-spiderbuf-inspired-") as tmp:
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
        and bool(plan.get("fix_intent"))
    )
    forbidden_count = _forbidden_output_count(output_text)
    expected_status = expected_verification.get("expected_status")
    actual_status = verification.get("status")

    return {
        "case_id": case_dir.name,
        "challenge_type": source.get("challenge_type"),
        "expected_category": ",".join(sorted(accepted_types)),
        "actual_category": actual_type,
        "expected_subtype": ",".join(sorted(accepted_subtypes)),
        "actual_subtype": actual_subtype,
        "diagnosis_result": "reasonable" if diagnosis_ok else "miss",
        "fix_plan_valid": fix_plan_valid,
        "verification_status_expected": expected_status,
        "verification_status_actual": actual_status,
        "verification_correct": actual_status == expected_status,
        "forbidden_output_count": forbidden_count,
        "local_only": source.get("local_only") is True,
        "safe_boundary": source.get("safe_boundary"),
    }


def _case_dirs() -> list[Path]:
    if not PACK_ROOT.exists():
        return []
    return sorted(path for path in PACK_ROOT.iterdir() if path.is_dir())


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


def _forbidden_output_count(text: str) -> int:
    return sum(text.count(term.lower()) for term in FORBIDDEN_OUTPUT_TERMS)


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    raise SystemExit(main())
