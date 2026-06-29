from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "public_failure_corpus" / "cases" / "v06_website_antibot.yaml"
DEFAULT_OUTPUT = ROOT / "validation" / "website_antibot_validation_50.json"
FORBIDDEN_OUTPUTS = (
    "bypass captcha",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate v0.6 website-change and anti-bot routing records.")
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS), help="Path to v06_website_antibot.yaml")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="Path to write validation JSON")
    args = parser.parse_args(argv)

    cases = _load_simple_yaml_documents(Path(args.corpus))
    results = _run_cases(cases)
    payload = _summarize(results)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = payload["summary"]
    print(
        "v0.6 validation: "
        f"{summary['reasonable_classifications']}/{summary['sample_count']} reasonable, "
        f"{summary['safe_next_actions']}/{summary['sample_count']} safe next actions, "
        f"forbidden_outputs={summary['forbidden_outputs']}"
    )
    return 0 if summary["forbidden_outputs"] == 0 else 1


def _load_simple_yaml_documents(path: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for raw_doc in path.read_text(encoding="utf-8").split("---"):
        case: dict[str, Any] = {}
        for raw_line in raw_doc.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ": " not in line:
                continue
            key, value = line.split(": ", 1)
            case[key] = _parse_scalar(value)
        if case:
            documents.append(case)
    return documents


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [part.strip().strip('"') for part in body.split(",")]
    if value in {"yes", "true"}:
        return True
    if value in {"no", "false"}:
        return False
    return value


def _run_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="afd-v06-validation-") as tmp:
        tmp_root = Path(tmp)
        for case in cases:
            input_dir = tmp_root / str(case["case_id"])
            output_dir = tmp_root / f"{case['case_id']}_report"
            input_dir.mkdir()
            (input_dir / "error.log").write_text(str(case.get("raw_error_excerpt", "")), encoding="utf-8")
            (input_dir / "user_description.txt").write_text(str(case.get("symptom", "")), encoding="utf-8")

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
            prompt = (output_dir / "codex_fix_prompt.md").read_text(encoding="utf-8")
            combined_output = json.dumps(diagnosis, ensure_ascii=False).lower() + "\n" + prompt.lower()
            expected = str(case.get("likely_technical_category", ""))
            actual = str(diagnosis.get("technical_category", ""))
            forbidden_hits = [phrase for phrase in FORBIDDEN_OUTPUTS if phrase in combined_output]
            results.append(
                {
                    "case_id": case.get("case_id"),
                    "source_url": case.get("source_url"),
                    "input_type": case.get("input_available", []),
                    "expected_category": expected,
                    "actual_category": actual,
                    "subtype": diagnosis.get("subtype"),
                    "failure_layer": diagnosis.get("failure_layer"),
                    "confidence": diagnosis.get("confidence"),
                    "reasonable_classification": actual == expected,
                    "safe_next_action": bool(diagnosis.get("safe_next_action")),
                    "codex_fix_prompt_generated": bool(prompt.strip()),
                    "forbidden_output_hits": forbidden_hits,
                    "misclassified": actual != expected,
                }
            )
            shutil.rmtree(output_dir, ignore_errors=True)
    return results


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = len(results)
    website_cases = [item for item in results if item["expected_category"] == "website_change"]
    anti_bot_cases = [item for item in results if item["expected_category"] == "anti_bot_risk"]
    reasonable = sum(1 for item in results if item["reasonable_classification"])
    safe_next_actions = sum(1 for item in results if item["safe_next_action"])
    forbidden = sum(len(item["forbidden_output_hits"]) for item in results)
    insufficient = sum(1 for item in results if item["actual_category"] == "insufficient_evidence")
    summary = {
        "sample_count": sample_count,
        "website_change_cases": len(website_cases),
        "anti_bot_risk_cases": len(anti_bot_cases),
        "reasonable_classifications": reasonable,
        "reasonable_classification_rate": round(reasonable / sample_count, 4) if sample_count else 0,
        "safe_next_actions": safe_next_actions,
        "safe_next_action_rate": round(safe_next_actions / sample_count, 4) if sample_count else 0,
        "forbidden_outputs": forbidden,
        "insufficient_evidence_cases": insufficient,
        "severe_misclassifications": sum(1 for item in results if item["misclassified"]),
    }
    return {
        "version": "v0.6.0",
        "scope": "Website Change + Anti-Bot Risk routing validation",
        "source_corpus": str(DEFAULT_CORPUS.relative_to(ROOT)).replace("\\", "/"),
        "record_type": "public-inspired sanitized records, not full real-world failure packages",
        "summary": summary,
        "cases": results,
    }


if __name__ == "__main__":
    raise SystemExit(main())
