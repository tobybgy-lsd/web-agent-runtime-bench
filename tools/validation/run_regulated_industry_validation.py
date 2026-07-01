from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from failure_doctor.regulated_industry import evaluate_regulated_suite


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "validation" / "regulated_industry_validation.json"


def run_validation() -> dict[str, Any]:
    payload = evaluate_regulated_suite("all")
    payload["version"] = "v3.6.0"
    payload["status"] = "pass" if _thresholds_pass(payload) else "fail"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def _thresholds_pass(payload: dict[str, Any]) -> bool:
    total = int(payload.get("total_cases", 0) or 0)
    return all(
        (
            payload.get("version") == "v3.6.0",
            total >= 220,
            payload.get("schema_valid") == total,
            payload.get("risk_classification_correct", 0) >= 215,
            payload.get("shareability_decision_correct", 0) >= 215,
            payload.get("pii_phi_detection_false_negative") == 0,
            payload.get("audit_chain_detection_correct", 0) >= 0.95,
            payload.get("ai_handoff_safety_correct", 0) >= 0.95,
            payload.get("ocr_document_safety_correct", 0) >= 0.95,
            payload.get("regulated_data_quality_correct", 0) >= 0.95,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
    )


def main() -> int:
    payload = run_validation()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
