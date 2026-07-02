from __future__ import annotations

from pathlib import Path
from typing import Any


def write_case_report(out: Path, payload: dict[str, Any]) -> None:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Failure Doctor Case Report",
        "",
        f"- status: {payload.get('status', payload.get('validation', {}).get('status', 'unknown'))}",
        f"- case_id: {payload.get('case_id', payload.get('issue_pack_id', 'unknown'))}",
        "- local_only: true",
        "- no_upload: true",
        "- public_safe: true",
        "",
    ]
    (out / "case_report.md").write_text("\n".join(lines), encoding="utf-8")
