from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .security import ConsoleSecurityError, assert_path_within_workspace, make_local_token, safe_join


REPORTS_DIR = "reports"
AUDIT_FILE = "audit.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def init_workspace(path: Path | str, *, host: str, port: int, readonly: bool = False) -> dict[str, Any]:
    root = Path(path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / REPORTS_DIR).mkdir(exist_ok=True)
    manifest = {
        "version": "v3.7.0",
        "workspace": str(root),
        "host": host,
        "port": port,
        "readonly": readonly,
        "local_only": True,
        "telemetry": "disabled",
        "external_assets": "disabled",
        "created_at": utc_now(),
        "token": make_local_token(),
    }
    manifest_path = root / "console_manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["token"] = previous.get("token") or manifest["token"]
        manifest["created_at"] = previous.get("created_at") or manifest["created_at"]
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def load_manifest(path: Path | str) -> dict[str, Any]:
    root = Path(path).expanduser().resolve()
    manifest_path = root / "console_manifest.json"
    if not manifest_path.exists():
        return init_workspace(root, host="127.0.0.1", port=8765)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def append_audit(workspace: Path | str, event: str, detail: dict[str, Any] | None = None) -> None:
    root = Path(workspace).expanduser().resolve()
    entry = {"time": utc_now(), "event": event, "detail": detail or {}}
    with (root / AUDIT_FILE).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_audit(workspace: Path | str, limit: int = 100) -> list[dict[str, Any]]:
    path = Path(workspace).expanduser().resolve() / AUDIT_FILE
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def report_id_from_path(path: Path) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in path.name)[:80] or "report"


def import_report(workspace: Path | str, report_path: Path | str, *, readonly: bool = False) -> dict[str, Any]:
    if readonly:
        raise ConsoleSecurityError("Console is running in read-only mode.")
    root = Path(workspace).expanduser().resolve()
    source = Path(report_path).expanduser().resolve()
    if not source.exists():
        raise ConsoleSecurityError("Report path does not exist.")
    if any(part.lower() == "raw_local_only_do_not_share" for part in source.parts):
        raise ConsoleSecurityError("Raw local-only evidence must not be imported into the console.")
    reports = safe_join(root, REPORTS_DIR)
    target = reports / report_id_from_path(source)
    if source.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target / source.name)
    assert_path_within_workspace(root, target)
    append_audit(root, "import_report", {"source": str(source), "target": str(target)})
    return {"report_id": target.name, "path": str(target)}


def list_report_dirs(workspace: Path | str) -> list[Path]:
    root = Path(workspace).expanduser().resolve()
    reports = safe_join(root, REPORTS_DIR)
    return sorted([item for item in reports.iterdir() if item.is_dir()])
