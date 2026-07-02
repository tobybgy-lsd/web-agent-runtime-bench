from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


RUNBOOK_FILES = {
    "runbook.md": "# Android Ops Runbook\n\nUse authorized, local-only, dry-run workflows by default.\n",
    "operator_checklist.md": "# Operator Checklist\n\n- Confirm authorized target.\n- Confirm dry-run mode.\n- Confirm no final submit.\n",
    "failure_triage.md": "# Failure Triage\n\nCheck device health, lease state, Appium session plan, UI dump, and sanitized logs.\n",
    "recovery_steps.md": "# Recovery Steps\n\nUse soft-reset, app-restart, or session-clean. Do not factory reset or root devices.\n",
    "manual_review_guide.md": "# Manual Review Guide\n\nReview uncertain locator, permission, keyboard, image picker, and disabled button failures.\n",
    "safety_boundary.md": "# Safety Boundary\n\nFinal submit and business mutation blocked by design unless explicitly approved and safety-passing.\n",
    "escalation.md": "# Escalation\n\nEscalate offline devices, repeated Appium failures, and business mutation requests to approved roles.\n",
}


def generate_runbook(run: Path, out: Path) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    for name, body in RUNBOOK_FILES.items():
        (out / name).write_text(body, encoding="utf-8")
    payload = {
        "schema_version": "android_runbook/v1",
        "status": "pass",
        "run": str(run),
        "files": sorted(RUNBOOK_FILES),
        "contains_bypass_guidance": False,
    }
    return write_json(out / "runbook_manifest.json", payload)

