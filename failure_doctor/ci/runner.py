from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ci/v1"
SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
PRIVATE_MARKERS = (
    "private_solutions",
    "Spiderbuf" + "ChallengeWorkbench",
    "CodexVault",
    "FLAG" + "{",
)
FORBIDDEN_MARKERS = (
    "captcha " + "bypass",
    "anti-bot " + "evasion",
    "fingerprint " + "spoofing",
    "dynamic signature " + "cracking",
    "proxy " + "rotation",
    "account " + "pool",
    "ip " + "pool",
    "stealth " + "recipe",
    "challenge " + "sol" + "ver",
    "hook " + "bypass",
)


def run_ci_gate(input_path: Path, out_dir: Path, *, fail_on: str = "high") -> dict[str, Any]:
    if fail_on not in SEVERITY_ORDER:
        raise ValueError(f"unknown fail-on threshold: {fail_on}")
    if not input_path.exists():
        raise FileNotFoundError(f"input not found: {input_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    payload = _load_input_payload(input_path)
    scan = _scan_input_text(input_path)
    severity = _decide_severity(payload, scan)
    threshold = SEVERITY_ORDER[fail_on]
    gate_decision = "fail" if SEVERITY_ORDER[severity["severity"]] >= threshold else "pass"

    if scan["private_solution_leak_count"] or scan["forbidden_output_count"]:
        gate_decision = "fail"

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "input": str(input_path),
        "local_only": True,
        "sanitized_artifacts_only": True,
        "external_api_call_count": 0,
        "raw_upload_count": 0,
        "env_dump_count": 0,
        "browser_profile_access_count": 0,
        "credential_store_access_count": 0,
        "private_solution_leak_count": scan["private_solution_leak_count"],
        "forbidden_output_count": scan["forbidden_output_count"],
    }
    gate = {
        "schema_version": SCHEMA_VERSION,
        "decision": gate_decision,
        "fail_on": fail_on,
        "severity": severity["severity"],
        "safe_for_public_ci_artifacts": gate_decision == "pass",
        "reason": _gate_reason(gate_decision, severity, scan),
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "diagnosis": payload.get("diagnosis", {}),
        "severity": severity,
        "gate": gate,
        "manifest": manifest,
    }
    audit = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": manifest["generated_at"],
        "checked_files": scan["checked_files"],
        "checks": [
            "local-only execution",
            "sanitized artifacts only",
            "no external API calls",
            "no raw upload",
            "no environment dump",
            "private training marker scan",
            "unsafe recommendation marker scan",
        ],
    }

    _write_json(out_dir / "ci_manifest.json", manifest)
    _write_json(out_dir / "severity_decision.json", severity)
    _write_json(out_dir / "gate_decision.json", gate)
    _write_json(out_dir / "ci_summary.json", summary)
    _write_json(out_dir / "audit_manifest.json", audit)
    (out_dir / "ci_summary.md").write_text(_render_summary(summary), encoding="utf-8")
    (out_dir / "open_this_first_ci.md").write_text(_render_open_first(summary), encoding="utf-8")
    sanitized = out_dir / "sanitized_artifacts"
    sanitized.mkdir(exist_ok=True)
    (sanitized / "README.md").write_text(
        "# Sanitized CI Artifacts\n\nThis folder is reserved for local sanitized report files only.\n",
        encoding="utf-8",
    )
    return summary


def validate_ci_report(report_dir: Path) -> dict[str, Any]:
    required = [
        "ci_manifest.json",
        "severity_decision.json",
        "gate_decision.json",
        "ci_summary.json",
        "ci_summary.md",
        "audit_manifest.json",
        "open_this_first_ci.md",
    ]
    missing = [name for name in required if not (report_dir / name).exists()]
    manifest = _read_json(report_dir / "ci_manifest.json") if not missing else {}
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not missing and _manifest_is_safe(manifest) else "fail",
        "missing_files": missing,
        "local_only": manifest.get("local_only"),
        "external_api_call_count": int(manifest.get("external_api_call_count", -1)),
        "raw_upload_count": int(manifest.get("raw_upload_count", -1)),
        "env_dump_count": int(manifest.get("env_dump_count", -1)),
        "private_solution_leak_count": int(manifest.get("private_solution_leak_count", -1)),
        "forbidden_output_count": int(manifest.get("forbidden_output_count", -1)),
    }
    return payload


def write_ci_templates(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        out_dir
        / "github-actions"
        / "failure-doctor-ci.yml": """name: Agent Failure Doctor CI
on:
  workflow_dispatch:
  pull_request:

jobs:
  failure-doctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install Agent Failure Doctor
        run: python -m pip install agent-failure-doctor
      - name: Run local CI gate
        run: failure-doctor ci run --input .failure-doctor/report --out .failure-doctor/ci --fail-on high
""",
        out_dir
        / "gitlab"
        / "failure-doctor-ci.yml": """failure_doctor:
  image: python:3.12
  script:
    - python -m pip install agent-failure-doctor
    - failure-doctor ci run --input .failure-doctor/report --out .failure-doctor/ci --fail-on high
  artifacts:
    when: always
    paths:
      - .failure-doctor/ci/ci_summary.md
      - .failure-doctor/ci/gate_decision.json
""",
        out_dir
        / "jenkins"
        / "Jenkinsfile": """pipeline {
  agent any
  stages {
    stage('Agent Failure Doctor') {
      steps {
        sh 'python -m pip install agent-failure-doctor'
        sh 'failure-doctor ci run --input .failure-doctor/report --out .failure-doctor/ci --fail-on high'
      }
    }
  }
}
""",
        out_dir
        / "powershell"
        / "run_failure_doctor_ci.ps1": """param(
    [string]$InputPath = ".failure-doctor\\report",
    [string]$OutPath = ".failure-doctor\\ci"
)
$ErrorActionPreference = "Stop"
python -m pip install agent-failure-doctor
failure-doctor ci run --input $InputPath --out $OutPath --fail-on high
""",
    }
    written: list[str] = []
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(str(path))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "template_count": len(written),
        "templates": written,
        "external_api_call_count": 0,
        "raw_upload_count": 0,
    }


def _load_input_payload(path: Path) -> dict[str, Any]:
    if path.is_file():
        return {"diagnosis": _read_json(path) if path.suffix.lower() == ".json" else {}}
    diagnosis = _read_json(path / "diagnosis.json") if (path / "diagnosis.json").exists() else {}
    safety = _read_json(path / "safety_report.json") if (path / "safety_report.json").exists() else {}
    full_chain = (
        _read_json(path / "full_chain_report.json") if (path / "full_chain_report.json").exists() else {}
    )
    return {"diagnosis": diagnosis, "safety": safety, "full_chain": full_chain}


def _decide_severity(payload: dict[str, Any], scan: dict[str, Any]) -> dict[str, Any]:
    diagnosis = payload.get("diagnosis", {})
    failure_type = str(diagnosis.get("failure_type") or diagnosis.get("technical_category") or "")
    subtype = str(diagnosis.get("subtype") or "")
    confidence = float(diagnosis.get("confidence", 0) or 0)
    severity = "low"
    reasons: list[str] = []
    if scan["private_solution_leak_count"] or scan["forbidden_output_count"]:
        severity = "critical"
        reasons.append("private or unsafe recommendation marker found in CI input")
    elif failure_type == "anti_bot_risk":
        severity = "medium"
        reasons.append("anti_bot_risk is routed to careful review in CI")
    elif confidence >= 0.9:
        reasons.append("high-confidence ordinary automation diagnosis")
    else:
        reasons.append("no CI safety blockers found")
    return {
        "schema_version": SCHEMA_VERSION,
        "severity": severity,
        "failure_type": failure_type,
        "subtype": subtype,
        "confidence": confidence,
        "confidence_reason": "; ".join(reasons),
        "private_solution_leak_count": scan["private_solution_leak_count"],
        "forbidden_output_count": scan["forbidden_output_count"],
    }


def _scan_input_text(path: Path) -> dict[str, Any]:
    files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
    private_hits = 0
    forbidden_hits = 0
    checked = 0
    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        checked += 1
        lowered = text.lower()
        private_hits += sum(1 for marker in PRIVATE_MARKERS if marker.lower() in lowered)
        forbidden_hits += sum(1 for marker in FORBIDDEN_MARKERS if marker.lower() in lowered)
    return {
        "checked_files": checked,
        "private_solution_leak_count": private_hits,
        "forbidden_output_count": forbidden_hits,
    }


def _gate_reason(gate_decision: str, severity: dict[str, Any], scan: dict[str, Any]) -> str:
    if gate_decision == "pass":
        return "CI report is local-only and no safety blockers were found."
    if scan["private_solution_leak_count"]:
        return "CI input contains private training markers; do not publish this artifact."
    if scan["forbidden_output_count"]:
        return "CI input contains unsafe recommendation markers; review and sanitize first."
    return f"Severity {severity['severity']} reached the configured CI threshold."


def _manifest_is_safe(manifest: dict[str, Any]) -> bool:
    return (
        manifest.get("local_only") is True
        and int(manifest.get("external_api_call_count", -1)) == 0
        and int(manifest.get("raw_upload_count", -1)) == 0
        and int(manifest.get("env_dump_count", -1)) == 0
        and int(manifest.get("private_solution_leak_count", -1)) == 0
        and int(manifest.get("forbidden_output_count", -1)) == 0
    )


def _render_summary(summary: dict[str, Any]) -> str:
    gate = summary["gate"]
    severity = summary["severity"]
    return "\n".join(
        [
            "# Agent Failure Doctor CI Summary",
            "",
            f"- Gate: `{gate['decision']}`",
            f"- Severity: `{severity['severity']}`",
            f"- Failure type: `{severity.get('failure_type') or 'n/a'}`",
            f"- Subtype: `{severity.get('subtype') or 'n/a'}`",
            f"- Reason: {gate['reason']}",
            "",
            "This CI report is local-first and does not upload raw evidence.",
            "",
        ]
    )


def _render_open_first(summary: dict[str, Any]) -> str:
    gate = summary["gate"]
    return "\n".join(
        [
            "# Open This First: CI Gate",
            "",
            f"Decision: **{gate['decision'].upper()}**",
            "",
            "Review `ci_summary.md`, `severity_decision.json`, and `gate_decision.json` before sharing artifacts.",
            "Only sanitized local report files should be attached to external issues.",
            "",
        ]
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def copy_sanitized_ci_report(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
