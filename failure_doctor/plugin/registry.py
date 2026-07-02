from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .manifest import load_manifest
from .validator import validate_plugin


TOOL_VERSION = "4.2.0"


def init_workspace(workspace: Path) -> Path:
    workspace = Path(workspace)
    for name in ("installed", "enabled", "disabled", "validation_reports", "security_reports", "exports", "cache"):
        (workspace / name).mkdir(parents=True, exist_ok=True)
    manifest = workspace / "plugin_workspace_manifest.json"
    if not manifest.exists():
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": "plugin_workspace/v1",
                    "tool_version": TOOL_VERSION,
                    "local_only": True,
                    "plugins_disabled_by_default": True,
                    "created_at": _now(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    registry = workspace / "registry.json"
    if not registry.exists():
        write_registry(workspace, [])
    audit(workspace, "workspace.init", {"workspace": str(workspace)})
    return workspace


def read_registry(workspace: Path) -> dict[str, Any]:
    init_workspace(workspace)
    return json.loads((Path(workspace) / "registry.json").read_text(encoding="utf-8"))


def write_registry(workspace: Path, plugins: list[dict[str, Any]]) -> None:
    Path(workspace).mkdir(parents=True, exist_ok=True)
    (Path(workspace) / "registry.json").write_text(
        json.dumps(
            {"schema_version": "plugin_registry/v1", "tool_version": TOOL_VERSION, "plugins": plugins},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def audit(workspace: Path, event: str, details: dict[str, Any]) -> None:
    init = Path(workspace)
    init.mkdir(parents=True, exist_ok=True)
    with (init / "audit_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": _now(), "event": event, "details": details}, ensure_ascii=False) + "\n")


def install_plugin(plugin_dir: Path, workspace: Path) -> dict[str, Any]:
    workspace = init_workspace(workspace)
    report = validate_plugin(plugin_dir)
    if report.get("status") != "pass":
        audit(workspace, "plugin.install.blocked", {"plugin_dir": str(plugin_dir), "report": report})
        raise ValueError("plugin validation failed; install blocked")
    manifest, _payload = load_manifest(plugin_dir)
    dest = workspace / "installed" / manifest.plugin_id
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(plugin_dir, dest)
    shutil.copy2(plugin_dir / "plugin_validation_report.json", workspace / "validation_reports" / f"{manifest.plugin_id}.json")
    registry = read_registry(workspace)
    plugins = [item for item in registry.get("plugins", []) if item.get("plugin_id") != manifest.plugin_id]
    plugins.append(
        {
            "plugin_id": manifest.plugin_id,
            "version": manifest.version,
            "type": manifest.type,
            "status": "disabled",
            "path": f"installed/{manifest.plugin_id}",
            "validation_status": "pass",
            "risk_level": report.get("risk_level"),
            "permissions": list(manifest.permissions),
        }
    )
    write_registry(workspace, plugins)
    audit(workspace, "plugin.install", {"plugin_id": manifest.plugin_id})
    return {"plugin_id": manifest.plugin_id, "workspace": str(workspace), "status": "installed"}


def enable_plugin(plugin_id: str, workspace: Path) -> dict[str, Any]:
    registry = read_registry(workspace)
    changed = False
    for item in registry.get("plugins", []):
        if item.get("plugin_id") == plugin_id:
            if item.get("validation_status") != "pass":
                raise ValueError("plugin validation pass required before enable")
            item["status"] = "enabled"
            changed = True
    if not changed:
        raise FileNotFoundError(f"plugin not installed: {plugin_id}")
    write_registry(workspace, registry["plugins"])
    audit(workspace, "plugin.enable", {"plugin_id": plugin_id})
    return {"plugin_id": plugin_id, "status": "enabled"}


def disable_plugin(plugin_id: str, workspace: Path) -> dict[str, Any]:
    registry = read_registry(workspace)
    changed = False
    for item in registry.get("plugins", []):
        if item.get("plugin_id") == plugin_id:
            item["status"] = "disabled"
            changed = True
    if not changed:
        raise FileNotFoundError(f"plugin not installed: {plugin_id}")
    write_registry(workspace, registry["plugins"])
    audit(workspace, "plugin.disable", {"plugin_id": plugin_id})
    return {"plugin_id": plugin_id, "status": "disabled"}


def get_plugin_dir(plugin_id: str, workspace: Path) -> Path:
    registry = read_registry(workspace)
    for item in registry.get("plugins", []):
        if item.get("plugin_id") == plugin_id:
            return Path(workspace) / str(item.get("path"))
    raise FileNotFoundError(f"plugin not installed: {plugin_id}")


def enabled_plugins(workspace: Path) -> list[dict[str, Any]]:
    return [item for item in read_registry(workspace).get("plugins", []) if item.get("status") == "enabled"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
