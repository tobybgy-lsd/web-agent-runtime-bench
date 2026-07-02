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
    "enterprise_governance": "enterprise_governance_validation.json",
    "role_based_console": "enterprise_governance_validation.json",
    "audit_ledger": "enterprise_governance_validation.json",
    "plugin_sdk_ecosystem": "plugin_sdk_ecosystem_validation.json",
    "plugin_security_sandbox": "plugin_sdk_ecosystem_validation.json",
    "adapter_extension_api": "plugin_sdk_ecosystem_validation.json",
    "real_user_case_program": "real_user_case_program_validation.json",
    "public_benchmark_pack": "public_benchmark_pack_validation.json",
    "desktop_rpa_adapter": "desktop_rpa_adapter_validation.json",
    "api_automation_adapter": "api_automation_adapter_validation.json",
    "mobile_automation_adapter": "mobile_automation_adapter_validation.json",
    "enterprise_deployment_hardening": "enterprise_deployment_hardening_validation.json",
    "backup_restore": "enterprise_deployment_hardening_validation.json",
    "offline_install": "enterprise_deployment_hardening_validation.json",
    "documentation_demo_adoption": "documentation_demo_adoption_validation.json",
    "stable_api_schema_plugin_abi": "stable_api_schema_plugin_abi_validation.json",
    "android_apk_ui_automation": "android_apk_automation_validation.json",
    "android_ui_tree_diagnostics": "android_apk_automation_validation.json",
    "mobile_flow_replay": "android_apk_automation_validation.json",
    "android_production_hardening": "android_production_hardening_validation.json",
    "android_locator_self_healing": "android_production_hardening_validation.json",
    "android_device_matrix_runner": "android_production_hardening_validation.json",
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
    if name in {"android_apk_ui_automation", "android_ui_tree_diagnostics", "mobile_flow_replay"}:
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 180,
            payload.get("schema_valid") == total,
            payload.get("ui_tree_dump_success", 0) >= 175,
            payload.get("screenshot_capture_success", 0) >= 170,
            payload.get("logcat_summary_success", 0) >= 175,
            payload.get("appium_dry_run_success", 0) >= 175,
            payload.get("locator_resolution_correct", 0) >= 170,
            payload.get("flow_validation_correct", 0) >= 175,
            payload.get("flow_replay_correct", 0) >= 170,
            payload.get("diagnosis_reasonable", 0) >= 170,
            payload.get("subtype_correct", 0) >= 165,
            payload.get("unsafe_flow_blocked") == payload.get("unsafe_flow_cases"),
            payload.get("final_submit_blocked_by_default") == payload.get("unsafe_flow_cases"),
            payload.get("external_api_call_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("active_probe_count") == 0,
            payload.get("browser_profile_access_count") == 0,
            payload.get("credential_store_access_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name in {"android_production_hardening", "android_locator_self_healing", "android_device_matrix_runner"}:
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 260,
            payload.get("schema_valid") == total,
            payload.get("app_profile_validation_correct", 0) >= 255,
            payload.get("page_object_generation_success", 0) >= 247,
            payload.get("locator_registry_validation_correct", 0) >= 255,
            payload.get("locator_self_healing_candidate_correct", 0) >= 247,
            payload.get("ui_tree_diff_correct", 0) >= 247,
            payload.get("flow_compile_success", 0) >= 255,
            payload.get("flow_lint_correct", 0) >= 255,
            payload.get("unsafe_flow_blocked") == payload.get("unsafe_flow_cases"),
            payload.get("absolute_coordinate_primary_blocked") == payload.get("unsafe_flow_cases"),
            payload.get("publish_guard_blocked_final_submit") == payload.get("unsafe_flow_cases"),
            payload.get("device_matrix_mock_success", 0) >= 247,
            payload.get("task_queue_checkpoint_success", 0) >= 247,
            payload.get("failure_replay_pack_created", 0) >= 255,
            payload.get("stability_score_generated", 0) >= 255,
            payload.get("console_android_pro_success", 0) >= 247,
            payload.get("ci_android_pro_success", 0) >= 247,
            payload.get("external_api_call_count") == 0,
            payload.get("screenshot_upload_count") == 0,
            payload.get("apk_modification_count") == 0,
            payload.get("hook_usage_count") == 0,
            payload.get("root_required_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("active_probe_count") == 0,
            payload.get("browser_profile_access_count") == 0,
            payload.get("credential_store_access_count") == 0,
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
    if name in {"enterprise_governance", "role_based_console", "audit_ledger"}:
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 180,
            payload.get("schema_valid") == total,
            payload.get("rbac_permission_correct", 0) >= int(total * 0.98),
            payload.get("unauthorized_action_blocked") == total,
            payload.get("approval_flow_correct", 0) >= int(total * 0.98),
            payload.get("audit_log_generated") == total,
            payload.get("audit_hash_chain_valid") == total,
            payload.get("policy_enforcement_correct", 0) >= int(total * 0.98),
            payload.get("console_rbac_correct", 0) >= int(total * 0.95),
            payload.get("ci_enterprise_policy_correct", 0) >= int(total * 0.95),
            payload.get("kb_enterprise_policy_correct", 0) >= int(total * 0.95),
            payload.get("reasoning_policy_correct", 0) >= int(total * 0.95),
            payload.get("raw_access_blocked_by_default") == total,
            payload.get("patch_auto_apply_available") is False,
            payload.get("external_api_call_count") == 0,
            payload.get("telemetry_call_count") == 0,
            payload.get("raw_secret_in_audit_export") == 0,
            payload.get("private_solution_in_workspace") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name in {"plugin_sdk_ecosystem", "plugin_security_sandbox", "adapter_extension_api"}:
        total = payload.get("total_cases", 0)
        conditions = (
            payload.get("status") == "pass",
            total >= 220,
            payload.get("schema_valid") == total,
            payload.get("manifest_validation_correct", 0) >= int(total * 0.98),
            payload.get("permission_enforcement_correct", 0) >= int(total * 0.98),
            payload.get("sandbox_path_guard_correct", 0) >= int(total * 0.98),
            payload.get("unsafe_plugin_blocked") == payload.get("negative_unsafe_plugin_cases"),
            payload.get("network_plugin_blocked_by_default") == payload.get("negative_unsafe_plugin_cases"),
            payload.get("shell_plugin_blocked_by_default") == payload.get("negative_unsafe_plugin_cases"),
            payload.get("raw_access_plugin_blocked_by_default") == payload.get("negative_unsafe_plugin_cases"),
            payload.get("private_solution_plugin_blocked") == payload.get("negative_unsafe_plugin_cases"),
            payload.get("forbidden_output_plugin_blocked") == payload.get("negative_unsafe_plugin_cases"),
            payload.get("scaffold_success", 0) >= int(total * 0.95),
            payload.get("install_enable_flow_correct", 0) >= int(total * 0.95),
            payload.get("hook_output_schema_valid", 0) >= int(total * 0.98),
            payload.get("console_plugin_rbac_correct", 0) >= int(total * 0.95),
            payload.get("ci_plugin_artifact_policy_correct", 0) >= int(total * 0.95),
            payload.get("enterprise_plugin_policy_correct", 0) >= int(total * 0.95),
            payload.get("external_api_call_count") == 0,
            payload.get("telemetry_call_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "real_user_case_program":
        conditions = (
            payload.get("status") == "pass",
            payload.get("case_intake_cases", 0) >= 120,
            payload.get("issue_pack_cases", 0) >= 40,
            payload.get("anonymization_success") == payload.get("case_intake_cases"),
            payload.get("publish_check_blocks_unsafe", 0) >= 20,
            payload.get("issue_pack_valid") == payload.get("issue_pack_cases"),
            payload.get("raw_secret_in_public_case") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "public_benchmark_pack":
        conditions = (
            payload.get("status") == "pass",
            payload.get("public_benchmark_cases", 0) >= 150,
            payload.get("regression_benchmark_cases", 0) >= 60,
            payload.get("runner_public_safe_status") == "pass",
            payload.get("runner_regression_status") == "pass",
            payload.get("suite_validation_public_safe") == "pass",
            payload.get("suite_validation_regression") == "pass",
            payload.get("compare_status") == "pass",
            payload.get("benchmark_artifacts_generated") is True,
            payload.get("forbidden_output_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("real_platform_access_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "desktop_rpa_adapter":
        conditions = (
            payload.get("status") == "pass",
            payload.get("desktop_rpa_cases", 0) >= 120,
            payload.get("normalization_success", 0) >= 118,
            payload.get("diagnosis_reasonable", 0) >= 114,
            payload.get("unsafe_guidance_count") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "api_automation_adapter":
        conditions = (
            payload.get("status") == "pass",
            payload.get("api_automation_cases", 0) >= 120,
            payload.get("normalization_success", 0) >= 118,
            payload.get("diagnosis_reasonable", 0) >= 114,
            payload.get("unsafe_guidance_count") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "mobile_automation_adapter":
        conditions = (
            payload.get("status") == "pass",
            payload.get("mobile_automation_cases", 0) >= 80,
            payload.get("normalization_success", 0) >= 78,
            payload.get("diagnosis_reasonable", 0) >= 76,
            payload.get("unsafe_guidance_count") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("real_platform_access_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name in {"enterprise_deployment_hardening", "backup_restore", "offline_install"}:
        conditions = (
            payload.get("status") == "pass",
            payload.get("backup_restore_cases", 0) >= 80,
            payload.get("migration_cases", 0) >= 60,
            payload.get("offline_bundle_cases", 0) >= 40,
            payload.get("backup_restore_success", 0) >= 0.98,
            payload.get("migration_dry_run_success", 0) >= 0.98,
            payload.get("offline_bundle_private_content") == 0,
            payload.get("audit_chain_preserved") == 1.0,
            payload.get("retention_policy_correct", 0) >= 0.95,
            payload.get("external_api_call_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "documentation_demo_adoption":
        conditions = (
            payload.get("status") == "pass",
            payload.get("required_docs_present") == 1.0,
            payload.get("quickstart_commands_valid") == 1.0,
            payload.get("sample_reports_public_safe") == 1.0,
            payload.get("no_raw_secret_in_docs") == 0,
            payload.get("no_private_solution_in_docs") == 0,
            payload.get("no_forbidden_recommendations") == 0,
            payload.get("broken_internal_links") == 0,
            payload.get("external_api_call_count") == 0,
        )
        return "pass" if all(conditions) else "fail"
    if name == "stable_api_schema_plugin_abi":
        conditions = (
            payload.get("status") == "pass",
            payload.get("api_contract_cases", 0) >= 100,
            payload.get("schema_compatibility_cases", 0) >= 150,
            payload.get("plugin_abi_cases", 0) >= 100,
            payload.get("migration_cases", 0) >= 80,
            payload.get("stable_cli_contract_pass") == 1.0,
            payload.get("stable_schema_registry_complete") == 1.0,
            payload.get("plugin_abi_contract_pass") == 1.0,
            payload.get("backward_compatibility_pass", 0) >= 0.98,
            payload.get("migration_guide_generated") is True,
            payload.get("deprecation_report_generated") is True,
            payload.get("breaking_change_without_major") == 0,
            payload.get("external_api_call_count") == 0,
            payload.get("private_solution_leak_count") == 0,
            payload.get("forbidden_output_count") == 0,
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
        if name in {"enterprise_governance", "role_based_console", "audit_ledger"}:
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "rbac_permission_correct": payload.get("rbac_permission_correct"),
                    "unauthorized_action_blocked": payload.get("unauthorized_action_blocked"),
                    "approval_flow_correct": payload.get("approval_flow_correct"),
                    "audit_log_generated": payload.get("audit_log_generated"),
                    "audit_hash_chain_valid": payload.get("audit_hash_chain_valid"),
                    "policy_enforcement_correct": payload.get("policy_enforcement_correct"),
                    "console_rbac_correct": payload.get("console_rbac_correct"),
                    "ci_enterprise_policy_correct": payload.get("ci_enterprise_policy_correct"),
                    "kb_enterprise_policy_correct": payload.get("kb_enterprise_policy_correct"),
                    "reasoning_policy_correct": payload.get("reasoning_policy_correct"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                    "telemetry_call_count": payload.get("telemetry_call_count"),
                    "raw_secret_in_audit_export": payload.get("raw_secret_in_audit_export"),
                }
            )
        if name in {"plugin_sdk_ecosystem", "plugin_security_sandbox", "adapter_extension_api"}:
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "manifest_validation_correct": payload.get("manifest_validation_correct"),
                    "permission_enforcement_correct": payload.get("permission_enforcement_correct"),
                    "sandbox_path_guard_correct": payload.get("sandbox_path_guard_correct"),
                    "unsafe_plugin_blocked": payload.get("unsafe_plugin_blocked"),
                    "network_plugin_blocked_by_default": payload.get("network_plugin_blocked_by_default"),
                    "shell_plugin_blocked_by_default": payload.get("shell_plugin_blocked_by_default"),
                    "raw_access_plugin_blocked_by_default": payload.get("raw_access_plugin_blocked_by_default"),
                    "scaffold_success": payload.get("scaffold_success"),
                    "hook_output_schema_valid": payload.get("hook_output_schema_valid"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                    "telemetry_call_count": payload.get("telemetry_call_count"),
                }
            )
        if name in {"android_apk_ui_automation", "android_ui_tree_diagnostics", "mobile_flow_replay"}:
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "ui_tree_dump_success": payload.get("ui_tree_dump_success"),
                    "locator_resolution_correct": payload.get("locator_resolution_correct"),
                    "flow_validation_correct": payload.get("flow_validation_correct"),
                    "flow_replay_correct": payload.get("flow_replay_correct"),
                    "unsafe_flow_blocked": payload.get("unsafe_flow_blocked"),
                    "unsafe_flow_cases": payload.get("unsafe_flow_cases"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                }
            )
        if name in {"android_production_hardening", "android_locator_self_healing", "android_device_matrix_runner"}:
            pillars[name].update(
                {
                    "cases": payload.get("total_cases"),
                    "app_profile_validation_correct": payload.get("app_profile_validation_correct"),
                    "locator_self_healing_candidate_correct": payload.get("locator_self_healing_candidate_correct"),
                    "flow_lint_correct": payload.get("flow_lint_correct"),
                    "unsafe_flow_blocked": payload.get("unsafe_flow_blocked"),
                    "unsafe_flow_cases": payload.get("unsafe_flow_cases"),
                    "device_matrix_mock_success": payload.get("device_matrix_mock_success"),
                    "external_api_call_count": payload.get("external_api_call_count"),
                }
            )
        if name == "real_user_case_program":
            pillars[name].update(
                {
                    "total_cases": (
                        (payload.get("case_intake_cases") or 0)
                        + (payload.get("issue_pack_cases") or 0)
                    ),
                    "case_intake_cases": payload.get("case_intake_cases"),
                    "issue_pack_cases": payload.get("issue_pack_cases"),
                    "anonymization_success": payload.get("anonymization_success"),
                    "publish_check_blocks_unsafe": payload.get("publish_check_blocks_unsafe"),
                    "issue_pack_valid": payload.get("issue_pack_valid"),
                }
            )
        if name == "public_benchmark_pack":
            pillars[name].update(
                {
                    "total_cases": (
                        (payload.get("public_benchmark_cases") or 0)
                        + (payload.get("regression_benchmark_cases") or 0)
                    ),
                    "public_benchmark_cases": payload.get("public_benchmark_cases"),
                    "regression_benchmark_cases": payload.get("regression_benchmark_cases"),
                    "runner_public_safe_status": payload.get("runner_public_safe_status"),
                    "runner_regression_status": payload.get("runner_regression_status"),
                    "compare_status": payload.get("compare_status"),
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
    release_docs_status = "pass" if (ROOT / "docs" / "RELEASE_NOTES_v5.2.0.md").exists() else "fail"
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
        "release_notes": "docs/RELEASE_NOTES_v5.2.0.md",
        "dashboard": "validation/dashboard.md",
    }
    if p95_status != "pass":
        blocking_failures.append(f"p95_core_triage_gate: status={p95_status}")
    if safety_status != "pass":
        blocking_failures.append("safety_boundary: forbidden/private/real-platform/active-probe/profile/credential count is non-zero")
    if release_docs_status != "pass":
        blocking_failures.append("release_docs_dashboard: missing docs/RELEASE_NOTES_v5.2.0.md")

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
        "version": "v5.2.0",
        "overall_status": overall_status,
        "final_p98_gate": True,
        "ecosystem_score_excluded": True,
        "controlled_maturity_score": controlled_maturity_score,
        "current_stable_line": "v5.2.0" if overall_status == "pass" else "v5.1.0",
        "previous_stable_line": "v5.1.0",
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
            "external user feedback",
            "ecosystem integrations",
            "long-term compatibility monitoring",
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
