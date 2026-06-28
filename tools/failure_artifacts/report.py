"""Markdown reports for failure artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def render_markdown_report(artifact: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> str:
    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", []))
    fixes = "\n".join(f"- {item}" for item in diagnosis.get("suggested_fix", []))
    safety = artifact.get("safety", {})
    sanitized = "yes" if safety.get("sanitized") else "no"
    credentials = "yes" if safety.get("contains_credentials") else "no"
    return "\n".join(
        [
            "# Failure Diagnosis Report",
            "",
            f"- Run ID: `{artifact.get('run_id', 'unknown')}`",
            f"- Tool: `{artifact.get('tool', 'unknown')}`",
            f"- Failure Type: `{diagnosis.get('failure_type', 'unknown')}`",
            f"- Subtype: `{diagnosis.get('subtype', 'n/a')}`",
            f"- Evidence Level: `{diagnosis.get('evidence_level', 'n/a')}`",
            f"- Confidence: `{diagnosis.get('confidence', 0)}`",
            f"- Sanitized: {sanitized}",
            f"- Contains credentials: {credentials}",
            "",
            "## Summary",
            "",
            artifact.get("summary", "No summary provided."),
            "",
            "## Evidence",
            "",
            evidence or "- No evidence generated.",
            "",
            "## Suggested Fix",
            "",
            fixes or "- Manual review required.",
            "",
            "## Safety",
            "",
            "- This report is generated from a sanitized or synthetic artifact.",
            "- Do not include cookies, tokens, passwords, or authorization headers in submitted packs.",
            "",
        ]
    )


def write_report(artifact: Mapping[str, Any], diagnosis: Mapping[str, Any], out_dir: Path | str) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "diagnosis_report.md"
    path.write_text(render_markdown_report(artifact, diagnosis), encoding="utf-8")
    return path
