from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .safety import evaluate_flow_safety


def _coerce_scalar(raw: str) -> Any:
    value = raw.strip().strip('"').strip("'")
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "none"}:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def _parse_minimal_yaml(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by public examples and tests.

    This intentionally avoids adding a hard dependency. If PyYAML is installed,
    load_flow uses it first; this fallback handles top-level scalars plus a
    ``steps`` list with nested ``locator``/``verify`` mappings.
    """

    root: dict[str, Any] = {}
    lines = [line.rstrip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("  "):
            i += 1
            continue
        if line == "steps:":
            steps: list[dict[str, Any]] = []
            i += 1
            current: dict[str, Any] | None = None
            while i < len(lines) and lines[i].startswith("  "):
                item = lines[i]
                stripped = item.strip()
                if stripped.startswith("- "):
                    current = {}
                    steps.append(current)
                    rest = stripped[2:]
                    if rest and ":" in rest:
                        key, value = rest.split(":", 1)
                        current[key.strip()] = _coerce_scalar(value)
                    i += 1
                    continue
                if current is None:
                    i += 1
                    continue
                if item.startswith("    ") and not item.startswith("      ") and ":" in stripped:
                    key, value = stripped.split(":", 1)
                    key = key.strip()
                    if value.strip():
                        current[key] = _coerce_scalar(value)
                        i += 1
                    else:
                        nested: dict[str, Any] = {}
                        i += 1
                        while i < len(lines) and lines[i].startswith("      "):
                            nkey, nvalue = lines[i].strip().split(":", 1)
                            nested[nkey.strip()] = _coerce_scalar(nvalue)
                            i += 1
                        current[key] = nested
                    continue
                i += 1
            root["steps"] = steps
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            root[key.strip()] = _coerce_scalar(value)
        i += 1
    return root


def load_flow(path: Path | str) -> dict[str, Any]:
    flow_path = Path(path)
    text = flow_path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(text)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass
    return _parse_minimal_yaml(text)


def validate_flow(flow: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if flow.get("schema_version") != "android_flow/v1":
        errors.append("schema_version_must_be_android_flow_v1")
    if not flow.get("flow_id"):
        errors.append("flow_id_required")
    if not flow.get("package_name"):
        errors.append("package_name_required")
    if not isinstance(flow.get("steps"), list):
        errors.append("steps_required")
    safety = evaluate_flow_safety(flow)
    status = "pass" if not errors and safety["status"] == "pass" else "blocked" if safety["status"] == "blocked" else "fail"
    return {
        "schema_version": "android_flow_validation/v1",
        "status": status,
        "flow_id": flow.get("flow_id"),
        "errors": errors,
        "safety": safety,
        "step_count": len(flow.get("steps") or []) if isinstance(flow.get("steps"), list) else 0,
    }


def validate_flow_file(path: Path | str) -> dict[str, Any]:
    flow = load_flow(path)
    return validate_flow(flow)
