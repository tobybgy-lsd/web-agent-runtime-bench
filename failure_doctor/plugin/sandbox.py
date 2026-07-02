from __future__ import annotations

from pathlib import Path

from .security import is_sensitive_path


class PluginSandboxError(ValueError):
    pass


def resolve_scoped_path(base: Path, candidate: Path) -> Path:
    base = Path(base).resolve()
    target = Path(candidate).resolve()
    if is_sensitive_path(target):
        raise PluginSandboxError(f"sensitive path blocked: {target}")
    if target.is_symlink():
        raise PluginSandboxError(f"symlink path blocked: {target}")
    if base != target and base not in target.parents:
        raise PluginSandboxError(f"path traversal blocked: {target}")
    return target


def validate_plugin_io(input_dir: Path, out_dir: Path) -> None:
    input_dir = Path(input_dir)
    out_dir = Path(out_dir)
    if is_sensitive_path(input_dir) or is_sensitive_path(out_dir):
        raise PluginSandboxError("sensitive plugin I/O path blocked")
    if ".." in input_dir.parts or ".." in out_dir.parts:
        raise PluginSandboxError("path traversal blocked")
