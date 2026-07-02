from __future__ import annotations

import json
from pathlib import Path

from .models import PluginManifest


def manifest_path(plugin_dir: Path) -> Path:
    return Path(plugin_dir) / "plugin_manifest.json"


def load_manifest(plugin_dir: Path) -> tuple[PluginManifest, dict]:
    path = manifest_path(plugin_dir)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return PluginManifest.from_mapping(payload), payload


def write_manifest(plugin_dir: Path, payload: dict) -> None:
    (plugin_dir / "plugin_manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
