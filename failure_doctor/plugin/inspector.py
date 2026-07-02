from __future__ import annotations

import json
from pathlib import Path

from .manifest import load_manifest
from .validator import validate_plugin


def inspect_plugin(plugin_dir: Path) -> dict:
    manifest, payload = load_manifest(Path(plugin_dir))
    validation = validate_plugin(Path(plugin_dir))
    return {
        "schema_version": "plugin_inspection/v1",
        "plugin_id": manifest.plugin_id,
        "type": manifest.type,
        "version": manifest.version,
        "permissions": list(manifest.permissions),
        "hooks": list(manifest.hooks),
        "validation_status": validation.get("status"),
        "risk_level": validation.get("risk_level"),
        "local_only": payload.get("local_only"),
        "no_upload": payload.get("no_upload"),
        "no_external_api": payload.get("no_external_api"),
    }


def write_inspection(plugin_dir: Path) -> dict:
    payload = inspect_plugin(plugin_dir)
    (Path(plugin_dir) / "plugin_inspection.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload
