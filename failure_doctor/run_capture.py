from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


REDACTION_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._~+/=-]+", "Authorization: Bearer [REDACTED_BEARER_TOKEN]"),
    (r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED_BEARER_TOKEN]"),
    (r"sk-[A-Za-z0-9]{12,}", "[REDACTED_API_KEY]"),
    (r"(?i)(api[_-]?key|token|password|secret)=([^\s&]+)", r"\1=[REDACTED_SECRET]"),
)


def capture_run(
    command: list[str],
    *,
    workspace: Path,
    run_id: str | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    if not command:
        raise ValueError("failure-doctor run requires a command after --")

    cwd = (cwd or Path.cwd()).resolve()
    run_id = run_id or utc_run_id()
    run_dir = workspace / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc)
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    ended_at = datetime.now(timezone.utc)

    redaction_report: dict[str, Any] = {"redacted_fields": [], "replacement_count": 0}
    command_text = redact_text(" ".join(command), redaction_report)
    stdout = redact_text(completed.stdout or "", redaction_report)
    stderr = redact_text(completed.stderr or "", redaction_report)

    write_text(run_dir / "command.txt", command_text)
    write_text(run_dir / "exit_code.txt", f"{completed.returncode}\n")
    write_text(run_dir / "stdout.log", stdout)
    write_text(run_dir / "stderr.log", stderr)
    write_json(
        run_dir / "environment.json",
        environment_payload(command, cwd, started_at, ended_at),
    )
    detected = detect_artifacts(cwd)
    write_json(run_dir / "detected_artifacts.json", detected)
    write_json(run_dir / "redaction_report.json", redaction_report)
    write_json(run_dir / "safe_to_share.json", safe_to_share_payload(redaction_report))
    write_json(run_dir / "input_summary.json", input_summary(completed.returncode, detected))
    write_text(run_dir / "verification_hint.md", verification_hint(completed.returncode))

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "exit_code": completed.returncode,
        "redaction_report": redaction_report,
        "detected_artifacts": detected,
    }


def write_shareable_zip(run_dir: Path) -> Path:
    zip_path = run_dir / "shareable_failure_pack.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file() or path == zip_path:
                continue
            archive.write(path, path.relative_to(run_dir).as_posix())
    return zip_path


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def redact_text(text: str, report: dict[str, Any]) -> str:
    redacted = text
    for pattern, replacement in REDACTION_PATTERNS:
        redacted, count = re.subn(pattern, replacement, redacted)
        if count:
            report["replacement_count"] += count
            report["redacted_fields"].append(pattern)
    return redacted


def environment_payload(
    command: list[str],
    cwd: Path,
    started_at: datetime,
    ended_at: datetime,
) -> dict[str, Any]:
    return {
        "schema_version": "failure-doctor-run-environment/v1",
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "cwd": str(cwd),
        "command_argc": len(command),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "executable": sys.executable,
        "env": {
            "CI": os.environ.get("CI"),
            "GITHUB_ACTIONS": os.environ.get("GITHUB_ACTIONS"),
            "OS": os.environ.get("OS"),
        },
    }


def detect_artifacts(cwd: Path) -> dict[str, Any]:
    patterns = {
        "trace_zip": ["**/trace.zip", "**/*trace*.zip"],
        "logs": ["**/*.log", "**/error*.txt", "**/console*.txt"],
        "network": ["**/network*.json"],
        "screenshots": ["**/*.png", "**/*.jpg", "**/*.jpeg"],
    }
    detected: dict[str, Any] = {"schema_version": "detected-artifacts/v1", "cwd": str(cwd)}
    for key, globs in patterns.items():
        found: list[str] = []
        for glob in globs:
            for path in cwd.glob(glob):
                if path.is_file() and ".git" not in path.parts and len(found) < 20:
                    found.append(str(path.relative_to(cwd)))
        detected[key] = sorted(set(found))
    return detected


def safe_to_share_payload(redaction_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "safe_to_share": False,
        "reason": (
            "Manual review required before sharing. v2.0 applies basic local redaction, "
            "but it does not prove the pack is free of private URLs, customer data, or secrets."
        ),
        "redaction_replacement_count": redaction_report.get("replacement_count", 0),
    }


def input_summary(exit_code: int, detected: dict[str, Any]) -> dict[str, Any]:
    evidence_priority = ["log"]
    if detected.get("trace_zip"):
        evidence_priority.insert(0, "trace_zip")
    if detected.get("network"):
        evidence_priority.append("network")
    if detected.get("screenshots"):
        evidence_priority.append("screenshot_metadata")
    return {
        "schema_version": "auto-capture-input-summary/v1",
        "exit_code": exit_code,
        "observed_evidence": {
            "stdout_log": 1,
            "stderr_log": 1,
            "detected_trace_zip": len(detected.get("trace_zip", [])),
            "detected_network_json": len(detected.get("network", [])),
            "detected_screenshots": len(detected.get("screenshots", [])),
        },
        "evidence_priority": evidence_priority,
        "missing_evidence": ["trace_zip", "network.json", "screenshot.png"],
        "guidance": "Captured command output automatically. Add trace.zip or network.json for stronger evidence when available.",
    }


def verification_hint(exit_code: int) -> str:
    if exit_code == 0:
        return "\n".join(
            [
                "# Verification Hint",
                "",
                "The wrapped command exited successfully.",
                "No diagnosis was generated because there was no failed run to triage.",
            ]
        )
    return "\n".join(
        [
            "# Verification Hint",
            "",
            "After applying a fix, rerun the same command with `failure-doctor run -- ...`.",
            "Then compare the before and after run folders with `failure-doctor verify` if both contain failure evidence.",
        ]
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
