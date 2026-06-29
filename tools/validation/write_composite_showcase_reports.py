from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OUT_ROOT = Path("sample_reports/composite_showcase")


CASES: dict[str, dict[str, Any]] = {
    "auth_redirect_plus_selector_timeout": {
        "primary": ("playwright_storage_state_context", "login_redirect_after_authenticated_action"),
        "secondary": ("selector_drift", "timeout_waiting_for_selector"),
        "edge": "auth redirect/login evidence blocks downstream selector diagnosis",
        "repair": ["Restore authenticated context or session state first.", "Re-run and inspect selector symptoms only after auth succeeds."],
        "verification_status": "partially_resolved",
    },
    "route_har_miss_plus_network_404": {
        "primary": ("playwright_route_mock_har", "har_not_found_or_not_loaded"),
        "secondary": ("network_http_error", "http_404"),
        "edge": "route/HAR miss can leak to live network and produce HTTP errors",
        "repair": ["Fix route/HAR/mock registration before the first matching request.", "Then validate response shape and parser behavior."],
        "verification_status": "resolved",
    },
    "antibot_challenge_plus_selector_timeout": {
        "primary": ("anti_bot_risk", "captcha_or_challenge_page"),
        "secondary": ("selector_drift", "timeout_waiting_for_selector"),
        "edge": "access-control boundary blocks downstream page selectors",
        "repair": ["Confirm authorization and use an official API, authorized export, manual review, or stop automation if access is unclear.", "Only after the compliant path is confirmed, re-run selectors."],
        "verification_status": "not_resolved",
    },
}


def build_case(case_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    primary_category, primary_subtype = spec["primary"]
    secondary_category, secondary_subtype = spec["secondary"]
    graph = {
        "schema_version": "evidence_graph/v1",
        "nodes": [
            {"id": "E1", "type": "primary_signal", "label": primary_category, "severity": "high", "supports": [primary_category]},
            {"id": "E2", "type": "downstream_signal", "label": secondary_category, "severity": "medium", "supports": [secondary_category]},
        ],
        "edges": [{"from": "E1", "to": "E2", "relation": "blocks", "confidence": 0.88, "reason": spec["edge"]}],
    }
    return {
        "schema_version": "composite_diagnosis/v1",
        "diagnosis_mode": "composite",
        "technical_category": primary_category,
        "failure_type": primary_category,
        "subtype": primary_subtype,
        "confidence": 0.9,
        "primary_failure": {
            "technical_category": primary_category,
            "subtype": primary_subtype,
            "confidence": 0.9,
            "evidence_ids": ["E1"],
        },
        "secondary_failures": [
            {
                "technical_category": secondary_category,
                "subtype": secondary_subtype,
                "relationship_to_primary": "blocked_by_primary",
                "evidence_ids": ["E2"],
            }
        ],
        "blocking_failure": {"technical_category": primary_category, "subtype": primary_subtype, "reason": spec["edge"], "evidence_ids": ["E1"]},
        "downstream_failures": [{"technical_category": secondary_category, "subtype": secondary_subtype, "caused_by": primary_category, "evidence_ids": ["E2"]}],
        "evidence_graph": graph,
        "repair_order": spec["repair"],
        "why_this_order": spec["edge"],
        "safe_next_action": True,
    }


def write_reports() -> dict[str, Any]:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for case_id, spec in CASES.items():
        case_dir = OUT_ROOT / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        diagnosis = build_case(case_id, spec)
        fix_plan = {
            "schema_version": "fix_plan/v1",
            "failure_type": diagnosis["technical_category"],
            "subtype": diagnosis["subtype"],
            "repair_order": diagnosis["repair_order"],
            "blocking_failure": diagnosis["blocking_failure"],
            "secondary_failures": diagnosis["secondary_failures"],
            "safe_next_action": True,
            "forbidden_actions": ["access-control defeat", "challenge automation", "credential extraction", "unauthorized collection"],
        }
        verification = {
            "schema_version": "verification_report/v1",
            "status": spec["verification_status"],
            "confidence": 0.82,
            "safe_next_action": True,
            "notes": ["Showcase verification report for composite repair-order behavior."],
        }
        (case_dir / "diagnosis.json").write_text(json.dumps(diagnosis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (case_dir / "evidence_graph.json").write_text(json.dumps(diagnosis["evidence_graph"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (case_dir / "fix_plan.json").write_text(json.dumps(fix_plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (case_dir / "verification_report.json").write_text(json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (case_dir / "diagnosis.md").write_text(_diagnosis_md(case_id, diagnosis), encoding="utf-8")
        (case_dir / "fix_plan.md").write_text(_fix_plan_md(fix_plan), encoding="utf-8")
        (case_dir / "verification_report.md").write_text(_verification_md(verification), encoding="utf-8")
        written.append(case_id)
    return {"version": "v2.4.1", "written": written, "status": "pass"}


def _diagnosis_md(case_id: str, diagnosis: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {case_id}",
            "",
            "## Primary Failure",
            f"- `{diagnosis['primary_failure']['technical_category']}` / `{diagnosis['primary_failure']['subtype']}`",
            "",
            "## Secondary Failures",
            f"- `{diagnosis['secondary_failures'][0]['technical_category']}` / `{diagnosis['secondary_failures'][0]['subtype']}`",
            "",
            "## Blocking Failure",
            f"- {diagnosis['blocking_failure']['reason']}",
            "",
            "## Repair Order",
            *[f"- {item}" for item in diagnosis["repair_order"]],
            "",
        ]
    )


def _fix_plan_md(plan: dict[str, Any]) -> str:
    return "# Fix Plan\n\n" + "\n".join(f"- {item}" for item in plan["repair_order"]) + "\n"


def _verification_md(report: dict[str, Any]) -> str:
    return f"# Verification\n\n- Status: `{report['status']}`\n- Confidence: `{report['confidence']}`\n"


def main() -> int:
    result = write_reports()
    print(f"composite showcase reports: {len(result['written'])} written, status={result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
