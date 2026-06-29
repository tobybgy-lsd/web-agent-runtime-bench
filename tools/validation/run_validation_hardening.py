from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "validation" / "v1_3_validation_hardening.json"


THRESHOLDS: dict[str, dict[str, float | int]] = {
    "template_fixtures": {
        "min_sample_count": 150,
        "min_reasonable_rate": 0.85,
        "min_actionable_rate": 0.90,
        "max_severe_misclassifications": 5,
        "max_forbidden_output_count": 0,
    },
    "public_inspired_independent": {
        "min_sample_count": 50,
        "min_reasonable_rate": 0.75,
        "min_actionable_rate": 0.85,
        "max_severe_misclassifications": 5,
        "max_forbidden_output_count": 0,
    },
    "real_playwright_trace_semantic": {
        "min_sample_count": 30,
        "min_reasonable_rate": 0.95,
        "min_actionable_rate": 0.95,
        "max_severe_misclassifications": 0,
        "max_forbidden_output_count": 0,
    },
    "website_change_antibot": {
        "min_sample_count": 50,
        "min_reasonable_rate": 0.95,
        "min_actionable_rate": 0.95,
        "max_severe_misclassifications": 0,
        "max_forbidden_output_count": 0,
    },
    "external_public_reference": {
        "min_sample_count": 20,
        "min_reasonable_rate": 0.90,
        "min_actionable_rate": 0.90,
        "max_severe_misclassifications": 1,
        "max_forbidden_output_count": 0,
    },
    "external_heldout_public_source": {
        "min_sample_count": 10,
        "min_reasonable_rate": 0.80,
        "min_actionable_rate": 0.90,
        "max_severe_misclassifications": 1,
        "max_forbidden_output_count": 0,
    },
    "resolution_validation": {
        "min_sample_count": 12,
        "min_status_correct_rate": 0.90,
        "min_actionable_rate": 0.90,
        "max_forbidden_output_count": 0,
    },
    "applied_scenario_validation": {
        "min_sample_count": 18,
        "min_reasonable_rate": 0.90,
        "min_fix_plan_rate": 0.95,
        "min_verification_correct_rate": 0.90,
        "max_forbidden_output_count": 0,
    },
    "integration_adapters": {
        "min_sample_count": 4,
        "min_reasonable_rate": 1.0,
        "min_actionable_rate": 1.0,
        "max_forbidden_output_count": 0,
    },
}


def main() -> int:
    tracks = build_tracks()
    thresholds = render_thresholds()
    backlog = build_regression_backlog()
    overall_gate = "pass" if all(track["gate"] == "pass" for track in tracks) else "fail"
    payload = {
        "schema_version": "validation-hardening/v1.3",
        "version": "v1.3",
        "purpose": (
            "Aggregate validation gates across evidence tiers without averaging synthetic, "
            "public-inspired, native-trace, resolution, scenario, and integration tracks."
        ),
        "overall_gate": overall_gate,
        "tracks": tracks,
        "thresholds": thresholds,
        "regression_backlog": backlog,
        "notes": [
            "There is intentionally no single averaged accuracy score.",
            "Each track keeps its own evidence tier, source file, metrics, and gate.",
            "Backlog entries default safe_to_publish=false until manually reviewed.",
        ],
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total_tracks = len(tracks)
    print(
        "validation hardening: "
        f"{sum(1 for track in tracks if track['gate'] == 'pass')}/{total_tracks} tracks pass, "
        f"regression_backlog={len(backlog)}, overall_gate={overall_gate}"
    )
    return 0 if overall_gate == "pass" else 1


def build_tracks() -> list[dict[str, Any]]:
    return [
        template_track(),
        public_inspired_track(),
        real_trace_track(),
        website_antibot_track(),
        external_public_reference_track(),
        external_heldout_track(),
        resolution_track(),
        applied_scenario_track(),
        integration_track(),
    ]


def template_track() -> dict[str, Any]:
    path = ROOT / "validation" / "public_failure_validation_150.json"
    data = read_json(path)
    metrics = data["metrics"]
    return classified_track(
        track_id="template_fixtures",
        evidence_tier="sanitized_template",
        source_file=rel(path),
        sample_count=metrics["sample_count"],
        reasonable=metrics["reasonable_classifications"],
        actionable=metrics["usable_next_actions"],
        severe=metrics["severe_misclassifications"],
        insufficient=metrics["insufficient_evidence_cases"],
        forbidden=0,
    )


def public_inspired_track() -> dict[str, Any]:
    path = ROOT / "validation" / "public_failure_validation_50.json"
    data = read_json(path)
    metrics = data["metrics"]
    return classified_track(
        track_id="public_inspired_independent",
        evidence_tier="public_inspired_sanitized",
        source_file=rel(path),
        sample_count=metrics["sample_count"],
        reasonable=metrics["reasonable_classifications"],
        actionable=metrics["usable_next_actions"],
        severe=metrics["severe_misclassifications"],
        insufficient=metrics["insufficient_evidence_cases"],
        forbidden=0,
    )


def real_trace_track() -> dict[str, Any]:
    path = ROOT / "validation" / "real_trace_validation_30.json"
    data = read_json(path)
    return classified_track(
        track_id="real_playwright_trace_semantic",
        evidence_tier="native_trace",
        source_file=rel(path),
        sample_count=data["total_cases"],
        reasonable=data["reasonable_category_match"],
        actionable=data["actionable_next_action"],
        severe=data["severe_misclassification"],
        insufficient=data["insufficient_evidence"],
        forbidden=data["forbidden_output_count"],
        exact_subtype_match=data["exact_subtype_match"],
    )


def website_antibot_track() -> dict[str, Any]:
    path = ROOT / "validation" / "website_antibot_validation_50.json"
    data = read_json(path)
    summary = data["summary"]
    return classified_track(
        track_id="website_change_antibot",
        evidence_tier="public_inspired_sanitized",
        source_file=rel(path),
        sample_count=summary["sample_count"],
        reasonable=summary["reasonable_classifications"],
        actionable=summary["safe_next_actions"],
        severe=summary["severe_misclassifications"],
        insufficient=summary["insufficient_evidence_cases"],
        forbidden=summary["forbidden_outputs"],
    )


def external_public_reference_track() -> dict[str, Any]:
    path = ROOT / "validation" / "external_heldout_20.json"
    data = read_json(path)
    summary = data["summary"]
    return classified_track(
        track_id="external_public_reference",
        evidence_tier="traceable_public_reference",
        source_file=rel(path),
        sample_count=summary["total_heldout_cases"],
        reasonable=summary["reasonable_category_match"],
        actionable=summary["actionable_next_action"],
        severe=summary["severe_misclassification"],
        insufficient=summary["insufficient_evidence"],
        forbidden=summary["forbidden_output_count"],
        exact_category_match=summary["exact_category_match"],
    )


def external_heldout_track() -> dict[str, Any]:
    path = ROOT / "validation" / "external_heldout_10.json"
    data = read_json(path)
    summary = data["summary"]
    return classified_track(
        track_id="external_heldout_public_source",
        evidence_tier="traceable_public_source",
        source_file=rel(path),
        sample_count=summary["sample_count"],
        reasonable=summary["reasonable_classifications"],
        actionable=summary["actionable_next_actions"],
        severe=summary["severe_misclassifications"],
        insufficient=summary["insufficient_evidence_cases"],
        forbidden=summary["forbidden_outputs"],
    )


def resolution_track() -> dict[str, Any]:
    path = ROOT / "validation" / "resolution_validation_12.json"
    data = read_json(path)
    summary = data["summary"]
    track = {
        "track_id": "resolution_validation",
        "evidence_tier": "before_after_local_fixture",
        "source_file": rel(path),
        "sample_count": summary["total_cases"],
        "status_correct": summary["correct_status"],
        "status_correct_rate": rate(summary["correct_status"], summary["total_cases"]),
        "actionable_next_action": summary["actionable_next_step"],
        "actionable_rate": rate(summary["actionable_next_step"], summary["total_cases"]),
        "forbidden_output_count": summary["forbidden_output_count"],
        "gate": "pending",
    }
    return with_gate(track)


def applied_scenario_track() -> dict[str, Any]:
    path = ROOT / "validation" / "applied_scenario_validation.json"
    data = read_json(path)
    track = {
        "track_id": "applied_scenario_validation",
        "evidence_tier": "local_applied_scenario",
        "source_file": rel(path),
        "sample_count": data["total_cases"],
        "reasonable_classification": data["diagnosis_reasonable"],
        "reasonable_rate": rate(data["diagnosis_reasonable"], data["total_cases"]),
        "fix_plan_valid": data["fix_plan_valid"],
        "fix_plan_rate": rate(data["fix_plan_valid"], data["total_cases"]),
        "verification_correct": data["verification_correct"],
        "verification_correct_rate": rate(data["verification_correct"], data["total_cases"]),
        "forbidden_output_count": data["forbidden_output_count"],
        "gate": "pending",
    }
    return with_gate(track)


def integration_track() -> dict[str, Any]:
    track = {
        "track_id": "integration_adapters",
        "evidence_tier": "workflow_smoke",
        "source_file": "docs/internal/CODEX_EXECUTION_REPORT_v1_2_INTEGRATION_PACK.md",
        "sample_count": 4,
        "reasonable_classification": 4,
        "reasonable_rate": 1.0,
        "actionable_next_action": 4,
        "actionable_rate": 1.0,
        "severe_misclassification": 0,
        "insufficient_evidence": 0,
        "forbidden_output_count": 0,
        "gate": "pending",
    }
    return with_gate(track)


def classified_track(
    *,
    track_id: str,
    evidence_tier: str,
    source_file: str,
    sample_count: int,
    reasonable: int,
    actionable: int,
    severe: int,
    insufficient: int,
    forbidden: int,
    **extra: Any,
) -> dict[str, Any]:
    track = {
        "track_id": track_id,
        "evidence_tier": evidence_tier,
        "source_file": source_file,
        "sample_count": sample_count,
        "reasonable_classification": reasonable,
        "reasonable_rate": rate(reasonable, sample_count),
        "actionable_next_action": actionable,
        "actionable_rate": rate(actionable, sample_count),
        "severe_misclassification": severe,
        "insufficient_evidence": insufficient,
        "forbidden_output_count": forbidden,
        "gate": "pending",
        **extra,
    }
    return with_gate(track)


def with_gate(track: dict[str, Any]) -> dict[str, Any]:
    rules = THRESHOLDS[track["track_id"]]
    failures: list[str] = []
    if int(track["sample_count"]) < int(rules.get("min_sample_count", 0)):
        failures.append("sample_count")
    if "min_reasonable_rate" in rules and float(track.get("reasonable_rate", 0)) < float(rules["min_reasonable_rate"]):
        failures.append("reasonable_rate")
    if "min_actionable_rate" in rules and float(track.get("actionable_rate", 0)) < float(rules["min_actionable_rate"]):
        failures.append("actionable_rate")
    if "min_status_correct_rate" in rules and float(track.get("status_correct_rate", 0)) < float(rules["min_status_correct_rate"]):
        failures.append("status_correct_rate")
    if "min_fix_plan_rate" in rules and float(track.get("fix_plan_rate", 0)) < float(rules["min_fix_plan_rate"]):
        failures.append("fix_plan_rate")
    if "min_verification_correct_rate" in rules and float(track.get("verification_correct_rate", 0)) < float(rules["min_verification_correct_rate"]):
        failures.append("verification_correct_rate")
    if int(track.get("severe_misclassification", 0)) > int(rules.get("max_severe_misclassifications", 999999)):
        failures.append("severe_misclassification")
    if int(track.get("forbidden_output_count", 0)) > int(rules.get("max_forbidden_output_count", 999999)):
        failures.append("forbidden_output_count")
    track["gate"] = "pass" if not failures else "fail"
    track["gate_failures"] = failures
    return track


def build_regression_backlog() -> list[dict[str, Any]]:
    backlog: list[dict[str, Any]] = []
    backlog.extend(backlog_from_validation_cases(ROOT / "validation" / "public_failure_validation_150.json", "template_fixtures"))
    backlog.extend(backlog_from_validation_cases(ROOT / "validation" / "public_failure_validation_50.json", "public_inspired_independent"))
    backlog.extend(backlog_from_external_heldout(ROOT / "validation" / "external_heldout_10.json", "external_heldout_public_source"))
    backlog.extend(backlog_from_external_reference(ROOT / "validation" / "external_heldout_20.json", "external_public_reference"))
    return backlog[:40]


def backlog_from_validation_cases(path: Path, track_id: str) -> list[dict[str, Any]]:
    data = read_json(path)
    items: list[dict[str, Any]] = []
    for case in data.get("cases", []):
        reason = ""
        if case.get("is_misclassified"):
            reason = "severe_misclassification"
        elif str(case.get("actual_category")) == "insufficient_evidence" or str(case.get("evidence_level")) == "low":
            reason = "insufficient_evidence"
        if reason:
            items.append(backlog_item(track_id, case.get("case_id"), reason, case))
    return items


def backlog_from_external_heldout(path: Path, track_id: str) -> list[dict[str, Any]]:
    data = read_json(path)
    items: list[dict[str, Any]] = []
    for case in data.get("cases", []):
        reason = ""
        if case.get("is_severe_misclassification"):
            reason = "severe_misclassification"
        elif not case.get("reasonable_classification"):
            reason = "insufficient_evidence"
        if reason:
            items.append(backlog_item(track_id, case.get("case_id"), reason, case))
    return items


def backlog_from_external_reference(path: Path, track_id: str) -> list[dict[str, Any]]:
    data = read_json(path)
    items: list[dict[str, Any]] = []
    for case in data.get("cases", []):
        result = case.get("result")
        if result in {"severe_misclassification", "insufficient_evidence"}:
            items.append(backlog_item(track_id, case.get("case_id"), str(result), case))
    return items


def backlog_item(track_id: str, case_id: Any, reason: str, case: dict[str, Any]) -> dict[str, Any]:
    return {
        "track_id": track_id,
        "case_id": str(case_id or "unknown"),
        "reason": reason,
        "expected_category": case.get("expected_category"),
        "actual_category": case.get("actual_category"),
        "source_url": case.get("source_url"),
        "safe_to_publish": False,
    }


def render_thresholds() -> list[dict[str, Any]]:
    return [{"track_id": track_id, **rules} for track_id, rules in THRESHOLDS.items()]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rate(value: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(value / total, 4)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
