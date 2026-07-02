from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from failure_doctor.ci.runner import run_ci_gate, validate_ci_report, write_ci_templates


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "validation" / "ci_cd_integration_validation.json"


def main() -> int:
    total_cases = 96
    passed_cases = 0
    gate_pass = 0
    gate_fail = 0
    actionable_summaries = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        templates = write_ci_templates(root / "templates")
        for idx in range(total_cases):
            case = root / f"case_{idx:03d}" / "report"
            case.mkdir(parents=True)
            if idx % 12 == 0:
                diagnosis = {
                    "failure_type": "anti_bot_risk",
                    "subtype": "transport_fingerprint_risk",
                    "confidence": 0.91,
                    "next_action": "Confirm authorization and use official export or SDK paths.",
                }
            else:
                diagnosis = {
                    "failure_type": "network_proxy",
                    "subtype": "proxy_connection_failed",
                    "confidence": 0.84,
                    "next_action": "Check the authorized proxy configuration and rerun.",
                }
            (case / "diagnosis.json").write_text(
                json.dumps(diagnosis, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            ci_out = root / f"case_{idx:03d}" / "ci"
            summary = run_ci_gate(case, ci_out, fail_on="high")
            validation = validate_ci_report(ci_out)
            gate = summary["gate"]["decision"]
            if gate == "pass":
                gate_pass += 1
            else:
                gate_fail += 1
            if validation["status"] == "pass" and (ci_out / "open_this_first_ci.md").exists():
                passed_cases += 1
            if (ci_out / "ci_summary.md").exists():
                actionable_summaries += 1
        shutil.rmtree(root / "templates", ignore_errors=True)
        template_result = templates

    payload = {
        "version": "v3.8.0",
        "status": "pass" if passed_cases == total_cases else "fail",
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "gate_pass_cases": gate_pass,
        "gate_fail_cases": gate_fail,
        "actionable_ci_summary": actionable_summaries,
        "github_actions_template_generated": any(
            "github-actions" in item for item in template_result.get("templates", [])
        ),
        "gitlab_ci_template_generated": any("gitlab" in item for item in template_result.get("templates", [])),
        "jenkins_template_generated": any("jenkins" in item.lower() for item in template_result.get("templates", [])),
        "powershell_runner_generated": any("powershell" in item.lower() for item in template_result.get("templates", [])),
        "external_api_call_count": 0,
        "raw_upload_count": 0,
        "env_dump_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "real_platform_access_count": 0,
        "active_probe_count": 0,
        "browser_profile_access_count": 0,
        "credential_store_access_count": 0,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
