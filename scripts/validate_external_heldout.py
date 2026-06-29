from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "validation" / "external_heldout_10_cases.json"
OUT_PATH = ROOT / "validation" / "external_heldout_10.json"

FORBIDDEN_OUTPUTS = (
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
    source = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = source["cases"]
    results = run_cases(cases)
    payload = summarize(source, results)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = payload["summary"]
    print(
        "external held-out validation: "
        f"{summary['reasonable_classifications']}/{summary['sample_count']} reasonable, "
        f"{summary['actionable_next_actions']}/{summary['sample_count']} actionable, "
        f"forbidden_outputs={summary['forbidden_outputs']}"
    )
    return 0 if summary["forbidden_outputs"] == 0 else 1


def run_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="afd-heldout-") as tmp:
        tmp_root = Path(tmp)
        for case in cases:
            input_dir = tmp_root / str(case["case_id"])
            output_dir = tmp_root / f"{case['case_id']}_report"
            input_dir.mkdir()
            (input_dir / "error.log").write_text(str(case["raw_error_excerpt"]), encoding="utf-8")
            (input_dir / "user_description.txt").write_text(str(case.get("notes", "")), encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(output_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=30,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stdout + completed.stderr)

            diagnosis = json.loads((output_dir / "diagnosis.json").read_text(encoding="utf-8"))
            combined = "\n".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in output_dir.iterdir()
                if path.suffix.lower() in {".md", ".json", ".txt"}
            ).lower()
            forbidden_hits = [term for term in FORBIDDEN_OUTPUTS if term in combined]
            actual = str(diagnosis.get("technical_category") or diagnosis.get("failure_type") or "unknown")
            expected = str(case["expected_category"])
            reasonable = actual == expected or (
                expected == "insufficient_evidence" and actual in {"unknown", "insufficient_evidence"}
            )
            actionable = bool(diagnosis.get("next_action") or diagnosis.get("suggested_fix"))
            results.append(
                {
                    "case_id": case["case_id"],
                    "source_url": case["source_url"],
                    "source_family": case["source_family"],
                    "input_type": case["input_type"],
                    "expected_category": expected,
                    "actual_category": actual,
                    "subtype": diagnosis.get("subtype"),
                    "confidence": diagnosis.get("confidence"),
                    "reasonable_classification": reasonable,
                    "actionable_next_action": actionable,
                    "codex_fix_prompt_generated": (output_dir / "codex_fix_prompt.md").exists(),
                    "forbidden_output_hits": forbidden_hits,
                    "is_severe_misclassification": not reasonable and actual not in {"unknown", "insufficient_evidence"},
                    "notes": case.get("notes", ""),
                }
            )
            shutil.rmtree(output_dir, ignore_errors=True)
    return results


def summarize(source: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    reasonable = sum(1 for item in results if item["reasonable_classification"])
    actionable = sum(1 for item in results if item["actionable_next_action"])
    forbidden = sum(len(item["forbidden_output_hits"]) for item in results)
    severe = sum(1 for item in results if item["is_severe_misclassification"])
    insufficient = sum(1 for item in results if item["actual_category"] in {"unknown", "insufficient_evidence"})
    return {
        "schema_version": "external-heldout/v0.8-results",
        "method": source["method"],
        "summary": {
            "sample_count": total,
            "reasonable_classifications": reasonable,
            "reasonable_classification_rate": round(reasonable / total, 4) if total else 0,
            "actionable_next_actions": actionable,
            "actionable_next_action_rate": round(actionable / total, 4) if total else 0,
            "severe_misclassifications": severe,
            "insufficient_evidence_cases": insufficient,
            "forbidden_outputs": forbidden,
        },
        "cases": results,
    }


if __name__ == "__main__":
    raise SystemExit(main())
