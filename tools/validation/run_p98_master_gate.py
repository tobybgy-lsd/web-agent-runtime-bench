from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DIR = ROOT / "validation"

PILLAR_FILES = {
    "knowledge_base": "knowledge_base_p98_validation.json",
    "crawler_coverage_matrix": "crawler_failure_coverage_matrix.json",
    "playwright_trace_doctor": "playwright_trace_p98_validation.json",
    "cross_framework_adapter": "cross_framework_p98_validation.json",
    "training_challenge_sedimentation": "training_challenge_p98_validation.json",
    "composite_counterfactual_diagnosis": "composite_counterfactual_p98_validation.json",
    "ai_handoff_patch_proposal": "ai_handoff_p98_validation.json",
    "batch_fleet_diagnosis": "batch_diagnosis_p98_validation.json",
    "sanitize_share_pack": "sanitize_share_p98_validation.json",
    "auto_collector_one_click": "auto_collector_validation.json",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pillar_status(name: str, payload: dict[str, Any]) -> str:
    if name == "crawler_coverage_matrix":
        categories = payload.get("categories", [])
        conditions = (
            len(categories) >= 24,
            payload.get("total_mapped_cases", 0) >= 300,
            payload.get("forbidden_output_count") == 0,
            payload.get("categories_below_90_percent_reasonable") == 0,
            isinstance(payload.get("gap_backlog"), list),
        )
        return "pass" if all(conditions) else "fail"
    return "pass" if payload.get("status") == "pass" else "fail"


def forbidden_count(payload: dict[str, Any]) -> int:
    return int(payload.get("forbidden_output_count", 0) or 0)


def private_leak_count(payload: dict[str, Any]) -> int:
    return int(payload.get("private_solution_leak_count", 0) or 0)


def real_platform_access_count(payload: dict[str, Any]) -> int:
    return int(payload.get("real_platform_access_count", 0) or 0)


def build_payload() -> dict[str, Any]:
    pillars: dict[str, Any] = {}
    blocking_failures: list[str] = []
    warnings: list[str] = []
    total_forbidden = 0
    total_private_leaks = 0
    total_real_access = 0

    for name, filename in PILLAR_FILES.items():
        path = VALIDATION_DIR / filename
        if not path.exists():
            pillars[name] = {"status": "fail", "missing_validation_file": filename}
            blocking_failures.append(f"{name}: missing {filename}")
            continue
        payload = read_json(path)
        status = pillar_status(name, payload)
        total_forbidden += forbidden_count(payload)
        total_private_leaks += private_leak_count(payload)
        total_real_access += real_platform_access_count(payload)
        pillars[name] = {
            "status": status,
            "validation_file": filename,
            "total_cases": payload.get(
                "total_cases", payload.get("total_mapped_cases", payload.get("total_patterns"))
            ),
            "forbidden_output_count": forbidden_count(payload),
            "private_solution_leak_count": private_leak_count(payload),
            "real_platform_access_count": real_platform_access_count(payload),
        }
        if status != "pass":
            blocking_failures.append(f"{name}: status={status}")

    p95_path = VALIDATION_DIR / "p95_core_triage_gate.json"
    if p95_path.exists():
        p95 = read_json(p95_path)
        p95_status = p95.get("overall_status")
    else:
        p95_status = "missing"
    safety_status = "pass" if total_forbidden == 0 and total_private_leaks == 0 and total_real_access == 0 else "fail"
    release_docs_status = "pass" if (ROOT / "docs" / "RELEASE_NOTES_v3.2.6.md").exists() else "fail"
    pillars["safety_boundary"] = {
        "status": safety_status,
        "forbidden_output_count": total_forbidden,
        "private_solution_leak_count": total_private_leaks,
        "real_platform_access_count": total_real_access,
    }
    pillars["release_docs_dashboard"] = {
        "status": release_docs_status,
        "release_notes": "docs/RELEASE_NOTES_v3.2.6.md",
        "dashboard": "validation/dashboard.md",
    }
    if p95_status != "pass":
        blocking_failures.append(f"p95_core_triage_gate: status={p95_status}")
    if safety_status != "pass":
        blocking_failures.append("safety_boundary: forbidden/private/real-platform count is non-zero")
    if release_docs_status != "pass":
        blocking_failures.append("release_docs_dashboard: missing docs/RELEASE_NOTES_v3.2.6.md")

    all_pillars_pass = all(pillar["status"] == "pass" for pillar in pillars.values())
    controlled_maturity_score = 98 if all_pillars_pass and p95_status == "pass" else 94
    overall_status = (
        "pass"
        if all_pillars_pass
        and p95_status == "pass"
        and controlled_maturity_score >= 98
        and total_forbidden == 0
        and total_private_leaks == 0
        and total_real_access == 0
        else "fail"
    )
    return {
        "version": "v3.2.6",
        "overall_status": overall_status,
        "final_p98_gate": True,
        "ecosystem_score_excluded": True,
        "controlled_maturity_score": controlled_maturity_score,
        "current_stable_line": "v3.2.6" if overall_status == "pass" else "v3.1.0",
        "previous_stable_line": "v3.1.0",
        "p95_core_triage_gate_status": p95_status,
        "pillars": pillars,
        "global_forbidden_output_count": total_forbidden,
        "global_private_solution_leak_count": total_private_leaks,
        "global_real_platform_access_count": total_real_access,
        "blocking_failures": blocking_failures,
        "warnings": warnings,
        "next_gaps": [
            "external adoption",
            "real user issue corpus",
            "optional local UI",
            "optional dry-run patch apply",
            "optional PyPI release",
        ],
    }


def main() -> int:
    payload = build_payload()
    path = VALIDATION_DIR / "p98_master_gate.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
