from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CASES_ROOT = ROOT / "examples" / "resolution_validation_cases"
RESULT_PATH = ROOT / "validation" / "resolution_validation_12.json"

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
    cases = sorted(path for path in CASES_ROOT.iterdir() if path.is_dir())
    with tempfile.TemporaryDirectory(prefix="afd-resolution-validation-") as tmp:
        out_root = Path(tmp)
        results = [run_case(case, out_root) for case in cases]
    summary = summarize(results)
    payload = {
        "schema_version": "resolution-validation/v1",
        "summary": summary,
        "cases": results,
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "resolution validation: "
        f"{summary['correct_status']}/{summary['total_cases']} correct, "
        f"forbidden_outputs={summary['forbidden_output_count']}"
    )
    return 0 if summary["forbidden_output_count"] == 0 and summary["correct_status"] >= 10 else 1


def run_case(case_dir: Path, out_root: Path) -> dict[str, Any]:
    expected = json.loads((case_dir / "expected_verification.json").read_text(encoding="utf-8"))
    out_dir = out_root / case_dir.name
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "failure_doctor",
            "verify",
            "--before",
            str(case_dir / "before"),
            "--after",
            str(case_dir / "after"),
            "--out",
            str(out_dir),
            "--create-regression",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=60,
    )
    if completed.returncode != 0:
        return {
            "case_id": case_dir.name,
            "expected_status": expected["status"],
            "actual_status": "runner_error",
            "status_correct": False,
            "actionable_next_step": False,
            "forbidden_output_hits": [],
            "error": (completed.stdout + completed.stderr)[-1000:],
        }

    report = json.loads((out_dir / "verification_report.json").read_text(encoding="utf-8"))
    markdown = (out_dir / "verification_report.md").read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in out_dir.iterdir()
        if path.suffix.lower() in {".json", ".md", ".txt"}
    ).lower()
    forbidden_hits = [term for term in FORBIDDEN_OUTPUTS if term.lower() in combined]
    actual = str(report.get("status"))
    return {
        "case_id": case_dir.name,
        "expected_status": expected["status"],
        "actual_status": actual,
        "status_correct": actual == expected["status"],
        "actionable_next_step": "Recommended Next Step" in markdown,
        "forbidden_output_hits": forbidden_hits,
        "regression_case_created": (out_dir / "regression_case.json").exists(),
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    return {
        "total_cases": total,
        "correct_status": sum(1 for item in results if item["status_correct"]),
        "resolved_correct": sum(1 for item in results if item["expected_status"] == "resolved" and item["status_correct"]),
        "not_resolved_correct": sum(1 for item in results if item["expected_status"] == "not_resolved" and item["status_correct"]),
        "changed_failure_correct": sum(1 for item in results if item["expected_status"] == "changed_failure" and item["status_correct"]),
        "insufficient_evidence_correct": sum(1 for item in results if item["expected_status"] == "insufficient_evidence" and item["status_correct"]),
        "actionable_next_step": sum(1 for item in results if item["actionable_next_step"]),
        "forbidden_output_count": sum(len(item["forbidden_output_hits"]) for item in results),
    }


if __name__ == "__main__":
    raise SystemExit(main())
