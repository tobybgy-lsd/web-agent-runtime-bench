"""Render GitHub issue drafts for sanitized failure packs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .doctor import inspect_failure_pack
from .schema import load_artifact


def write_issue_draft(
    pack_dir: Path | str,
    out_path: Path | str | None = None,
    *,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    root = Path(pack_dir)
    doctor_report = inspect_failure_pack(root)
    if not doctor_report.get("ready") and not allow_incomplete:
        return {
            "ok": False,
            "error": "Pack is not ready. Run `warb doctor <pack_dir>` and fix reported issues first.",
            "doctor": doctor_report,
        }

    artifact_path = root / "failure_artifact.json"
    if not artifact_path.exists():
        return {
            "ok": False,
            "error": "missing failure_artifact.json",
            "doctor": doctor_report,
        }

    artifact = load_artifact(artifact_path)
    diagnosis = doctor_report.get("diagnosis", {})
    target = Path(out_path) if out_path else root / "github_issue.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_issue_draft(artifact, diagnosis, doctor_report), encoding="utf-8")
    return {
        "ok": True,
        "issue_path": str(target),
        "doctor": doctor_report,
        "diagnosis": diagnosis,
    }


def render_issue_draft(artifact: Mapping[str, Any], diagnosis: Mapping[str, Any], doctor_report: Mapping[str, Any]) -> str:
    failure_type = diagnosis.get("failure_type", "unknown")
    confidence = float(diagnosis.get("confidence", 0))
    evidence = _bullets(diagnosis.get("evidence", []), fallback="No classifier evidence extracted yet.")
    fixes = _bullets(diagnosis.get("suggested_fix", []), fallback="Needs maintainer triage.")
    checks = _doctor_checks(doctor_report.get("checks", []))
    issues = _bullets(doctor_report.get("errors", []), fallback="No blocking doctor issues.")
    next_steps = _bullets(doctor_report.get("next_steps", []), fallback="Review the pack before sharing.")
    files = _included_files(artifact)

    return f"""# Failure Pack: {artifact.get("run_id", "unknown")}

## Summary
{artifact.get("summary", "")}

## Initial Diagnosis
- Failure type: `{failure_type}`
- Confidence: `{confidence:.0%}`
- Tool: `{artifact.get("tool", "unknown")}`

## Doctor Check
- Pack health: `{"ready" if doctor_report.get("ready") else "needs attention"}`
{checks}

## Evidence
{evidence}

## Suggested Fix Direction
{fixes}

## Included Files
{files}
- `failure_artifact.json`

## Doctor Issues
{issues}

## Maintainer Next Steps
{next_steps}

## Safety Checklist
- [x] The pack is sanitized.
- [x] No cookies, tokens, passwords, or authorization headers are included.
- [x] No live endpoint or network replay is required.
- [x] No CAPTCHA bypass or anti-bot evasion request is included.
- [ ] I reviewed the generated issue before submitting.
"""


def _bullets(items: Any, *, fallback: str) -> str:
    if not isinstance(items, list) or not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def _doctor_checks(checks: Any) -> str:
    if not isinstance(checks, list) or not checks:
        return "- No doctor checks were available."
    lines = []
    for check in checks:
        if not isinstance(check, Mapping):
            continue
        lines.append(f"- `{check.get('status', 'info')}` {check.get('name', 'check')}: {check.get('detail', '')}")
    return "\n".join(lines) if lines else "- No doctor checks were available."


def _included_files(artifact: Mapping[str, Any]) -> str:
    refs = artifact.get("artifacts", {})
    if not isinstance(refs, Mapping) or not refs:
        return "- `failure_artifact.json`"
    return "\n".join(f"- `{path}`" for path in sorted(str(path) for path in refs.values() if path))
