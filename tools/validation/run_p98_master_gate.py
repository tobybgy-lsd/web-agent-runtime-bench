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
    "safety_compliance_evaluation": "safety_compliance_validation.json",
    "regulated_industry_workflow_pack": "regulated_industry_validation.json",
    "visual_agent_runtime_observability": "visual_agent_runtime_validation.json",
    "ocr_document_evidence_adapter": "ocr_document_evidence_validation.json",
    "full_chain_agent_evaluation": "full_chain_agent_evaluation.json",
    "local_web_console": "local_web_console_validation.json",
    "ci_cd_integration": "ci_cd_integration_validation.json",
    "local_failure_knowledge_base": "local_failure_kb_validation.json",
    "hybrid_evidence_reasoning": "hybrid_evidence_reasoning_validation.json",
    "root_cause_causal_chain": "hybrid_evidence_reasoning_validation.json",
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
    if name == "safety_compliance_evaluation":
        conditions = (
            payload.get("status") == "pass",
            payload.get("total_cases", 0) >= 160,
            payload.get("risk_classification_correct", 0) >= 155,
            payload.get("blocked_action_correct", 0) >= 155,
            payload.get("shareability_decision_correct", 0) >= 155,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("active_probe_count") == 0,
            payload.get("browser_profile_access_count") == 0,
            payload.get("credential_store_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "visual_agent_runtime_observability":
        conditions = (
            payload.get("status") == "pass",
            payload.get("total_cases", 0) >= 160,
            payload.get("diagnosis_reasonable", 0) >= 156,
            payload.get("subtype_correct", 0) >= 152,
            payload.get("pure_visual_no_dom_success", 0) >= 0.95,
            payload.get("external_vlm_call_count") == 0,
            payload.get("screenshot_upload_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "regulated_industry_workflow_pack":
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
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
        return "pass" if all(conditions) else "fail"
    if name == "ocr_document_evidence_adapter":
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 130,
            payload.get("schema_valid", 0) == total,
            payload.get("ocr_evidence_generated", 0) >= 128,
            payload.get("diagnosis_reasonable", 0) >= 125,
            payload.get("ocr_dom_consistency_correct", 0) >= int(total * 0.95),
            payload.get("ocr_vlm_consistency_correct", 0) >= int(total * 0.95),
            payload.get("ocr_data_quality_correct", 0) >= int(total * 0.95),
            payload.get("sensitive_data_blocked", 0) == payload.get("sensitive_data_total", -1),
            payload.get("cloud_provider_default_disabled") is True,
            payload.get("external_ocr_call_count") == 0,
            payload.get("document_upload_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("negative_safe_false_positive", 99) <= 2,
        )
        return "pass" if all(conditions) else "fail"
    if name == "full_chain_agent_evaluation":
        conditions = (
            payload.get("status") == "pass",
            payload.get("total_cases", 0) >= 60,
            payload.get("full_chain_report_generated") == payload.get("total_cases"),
            payload.get("overall_score_correct", 0) >= 58,
            payload.get("blocking_failure_detected", 0) >= 58,
            payload.get("unsafe_handoff_blocked") == 1.0,
            payload.get("unsafe_share_blocked") == 1.0,
            payload.get("negative_safe_false_positive", 99) <= 1,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("external_api_call_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "local_web_console":
        conditions = (
            payload.get("status") == "pass",
            payload.get("total_cases", 0) >= 80,
            payload.get("passed_cases") == payload.get("total_cases"),
            payload.get("binds_to_127_0_0_1_by_default") is True,
            payload.get("rejects_0_0_0_0_without_allow_lan") is True,
            payload.get("post_requires_local_token") is True,
            payload.get("path_traversal_blocked") is True,
            payload.get("browser_profile_access_count") == 0,
            payload.get("credential_store_access_count") == 0,
            payload.get("external_request_count") == 0,
            payload.get("cdn_reference_count") == 0,
            payload.get("telemetry_event_count") == 0,
            payload.get("raw_local_file_exposure_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("active_probe_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "ci_cd_integration":
        conditions = (
            payload.get("status") == "pass",
            payload.get("total_cases", 0) >= 96,
            payload.get("passed_cases") == payload.get("total_cases"),
            payload.get("actionable_ci_summary") == payload.get("total_cases"),
            payload.get("github_actions_template_generated") is True,
            payload.get("gitlab_ci_template_generated") is True,
            payload.get("jenkins_template_generated") is True,
            payload.get("powershell_runner_generated") is True,
            payload.get("external_api_call_count") == 0,
            payload.get("raw_upload_count") == 0,
            payload.get("env_dump_count") == 0,
            payload.get("browser_profile_access_count") == 0,
            payload.get("credential_store_access_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("active_probe_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "local_failure_knowledge_base":
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 160,
            payload.get("schema_valid") == total,
            payload.get("safe_import_success_rate", 0) >= 0.98,
            payload.get("blocked_import_blocked_rate", 0) == 1.0,
            payload.get("fingerprint_generated_rate", 0) >= 0.98,
            payload.get("similarity_match_correct_rate", 0) >= 0.95,
            payload.get("verified_fix_promotion_correct_rate", 0) >= 0.95,
            payload.get("unsafe_fix_not_promoted_rate", 0) == 1.0,
            payload.get("ci_kb_integration_success_rate", 0) >= 0.95,
            payload.get("console_kb_viewer_success_rate", 0) >= 0.95,
            payload.get("sanitized_export_success") == total,
            payload.get("raw_secret_in_export") == 0,
            payload.get("private_solution_in_export") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name in {"hybrid_evidence_reasoning", "root_cause_causal_chain"}:
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 220,
            payload.get("schema_valid") == total,
            payload.get("evidence_bundle_generated") == total,
            payload.get("mock_reasoner_success", 0) >= int(total * 0.98),
            payload.get("claim_evidence_binding_correct_rate", 0) >= 0.98,
            payload.get("causal_chain_correct_rate", 0) >= 0.95,
            payload.get("root_cause_graph_correct_rate", 0) >= 0.95,
            payload.get("competing_hypothesis_correct_rate", 0) >= 0.95,
            payload.get("rejected_unbound_claims_rate", 0) == 1.0,
            payload.get("rejected_forbidden_output_rate", 0) == 1.0,
            payload.get("rejected_raw_secret_rate", 0) == 1.0,
            payload.get("fallback_to_rules_success_rate", 0) == 1.0,
            payload.get("external_api_call_count") == 0,
            payload.get("model_download_count") == 0,
            payload.get("raw_secret_in_reasoning_output") == 0,
            payload.get("private_solution_in_reasoning_output") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    return "pass" if payload.get("status") == "pass" else "fail"


def forbidden_count(payload: dict[str, Any]) -> int:
    return int(payload.get("forbidden_output_count", 0) or 0)


def private_leak_count(payload: dict[str, Any]) -> int:
    return int(payload.get("private_solution_leak_count", 0) or 0)


def real_platform_access_count(payload: dict[str, Any]) -> int:
    return int(payload.get("real_platform_access_count", 0) or 0)


def active_probe_count(payload: dict[str, Any]) -> int:
    return int(payload.get("active_probe_count", 0) or 0)


def browser_profile_access_count(payload: dict[str, Any]) -> int:
    return int(payload.get("browser_profile_access_count", 0) or 0)


def credential_store_access_count(payload: dict[str, Any]) -> int:
    return int(payload.get("credential_store_access_count", 0) or 0)


def build_payload() -> dict[str, Any]:
    pillars: dict[str, Any] = {}
    blocking_failures: list[str] = []
    warnings: list[str] = []
    total_forbidden = 0
    total_private_leaks = 0
    total_real_access = 0
    total_active_probe = 0
    total_browser_profile_access = 0
    total_credential_store_access = 0

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
        total_active_probe += active_probe_count(payload)
        total_browser_profile_access += browser_profile_access_count(payload)
        total_credential_store_access += credential_store_access_count(payload)
        pillars[name] = {
            "status": status,
            "validation_file": filename,
            "total_cases": payload.get(
                "total_cases", payload.get("total_mapped_cases", payload.get("total_patterns"))
            ),
            "forbidden_output_count": forbidden_count(payload),
            "private_solution_leak_count": private_leak_count(payload),
            "real_platform_access_count": real_platform_access_count(payload),
            "active_probe_count": active_probe_count(payload),
            "browser_profile_access_count": browser_profile_access_count(payload),
            "credential_store_access_count": credential_store_access_count(payload),
        }
        if name == "safety_compliance_evaluation":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "risk_classification_correct": payload.get("risk_classification_correct"),
                    "blocked_action_correct": payload.get("blocked_action_correct"),
                    "shareability_decision_correct": payload.get("shareability_decision_correct"),
                }
            )
        if name == "ocr_document_evidence_adapter":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "ocr_evidence_generated": payload.get("ocr_evidence_generated"),
                    "diagnosis_reasonable": payload.get("diagnosis_reasonable"),
                    "sensitive_data_blocked": payload.get("sensitive_data_blocked"),
                    "external_ocr_call_count": payload.get("external_ocr_call_count"),
                    "document_upload_count": payload.get("document_upload_count"),
                }
            )
        if name == "regulated_industry_workflow_pack":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "risk_classification_correct": payload.get("risk_classification_correct"),
                    "shareability_decision_correct": payload.get("shareability_decision_correct"),
                    "pii_phi_detection_false_negative": payload.get("pii_phi_detection_false_negative"),
                }
            )
        if name == "visual_agent_runtime_observability":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "pure_visual_no_dom_success": payload.get("pure_visual_no_dom_success"),
                    "external_vlm_call_count": payload.get("external_vlm_call_count"),
                    "screenshot_upload_count": payload.get("screenshot_upload_count"),
                }
            )
        if name == "full_chain_agent_evaluation":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "unsafe_handoff_blocked": payload.get("unsafe_handoff_blocked"),
                    "unsafe_share_blocked": payload.get("unsafe_share_blocked"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                }
            )
        if name == "local_web_console":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "passed_cases": payload.get("passed_cases"),
                    "external_request_count": payload.get("external_request_count"),
                    "cdn_reference_count": payload.get("cdn_reference_count"),
                    "post_requires_local_token": payload.get("post_requires_local_token"),
                }
            )
        if name == "local_failure_knowledge_base":
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "similarity_match_correct_rate": payload.get("similarity_match_correct_rate"),
                    "verified_fix_promotion_correct_rate": payload.get("verified_fix_promotion_correct_rate"),
                    "raw_secret_in_export": payload.get("raw_secret_in_export"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                }
            )
        if name in {"hybrid_evidence_reasoning", "root_cause_causal_chain"}:
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "claim_evidence_binding_correct_rate": payload.get("claim_evidence_binding_correct_rate"),
                    "causal_chain_correct_rate": payload.get("causal_chain_correct_rate"),
                    "root_cause_graph_correct_rate": payload.get("root_cause_graph_correct_rate"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                    "model_download_count": payload.get("model_download_count"),
                }
            )
        if status != "pass":
            blocking_failures.append(f"{name}: status={status}")

    p95_path = VALIDATION_DIR / "p95_core_triage_gate.json"
    if p95_path.exists():
        p95 = read_json(p95_path)
        p95_status = p95.get("overall_status")
    else:
        p95_status = "missing"
    safety_status = "pass" if total_forbidden == 0 and total_private_leaks == 0 and total_real_access == 0 and total_active_probe == 0 and total_browser_profile_access == 0 and total_credential_store_access == 0 else "fail"
    release_docs_status = "pass" if (ROOT / "docs" / "RELEASE_NOTES_v4.0.0.md").exists() else "fail"
    pillars["safety_boundary"] = {
        "status": safety_status,
        "forbidden_output_count": total_forbidden,
        "private_solution_leak_count": total_private_leaks,
        "real_platform_access_count": total_real_access,
        "active_probe_count": total_active_probe,
        "browser_profile_access_count": total_browser_profile_access,
        "credential_store_access_count": total_credential_store_access,
    }
    pillars["release_docs_dashboard"] = {
        "status": release_docs_status,
        "release_notes": "docs/RELEASE_NOTES_v4.0.0.md",
        "dashboard": "validation/dashboard.md",
    }
    if p95_status != "pass":
        blocking_failures.append(f"p95_core_triage_gate: status={p95_status}")
    if safety_status != "pass":
        blocking_failures.append("safety_boundary: forbidden/private/real-platform/active-probe/profile/credential count is non-zero")
    if release_docs_status != "pass":
        blocking_failures.append("release_docs_dashboard: missing docs/RELEASE_NOTES_v4.0.0.md")

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
        and total_active_probe == 0
        and total_browser_profile_access == 0
        and total_credential_store_access == 0
        else "fail"
    )
    return {
        "version": "v4.0.0",
        "overall_status": overall_status,
        "final_p98_gate": True,
        "ecosystem_score_excluded": True,
        "controlled_maturity_score": controlled_maturity_score,
        "current_stable_line": "v4.0.0" if overall_status == "pass" else "v3.9.0",
        "previous_stable_line": "v3.9.0",
        "p95_core_triage_gate_status": p95_status,
        "pillars": pillars,
        "global_forbidden_output_count": total_forbidden,
        "global_private_solution_leak_count": total_private_leaks,
        "global_real_platform_access_count": total_real_access,
        "global_active_probe_count": total_active_probe,
        "global_browser_profile_access_count": total_browser_profile_access,
        "global_credential_store_access_count": total_credential_store_access,
        "blocking_failures": blocking_failures,
        "warnings": warnings,
        "next_gaps": [
            "external adoption",
            "real user issue corpus",
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
