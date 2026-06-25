"""Failure artifact loading and lightweight schema validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

REQUIRED_TOP_LEVEL = (
    "schema_version",
    "run_id",
    "tool",
    "target_type",
    "summary",
    "error",
    "artifacts",
    "observations",
    "expected",
    "actual",
    "labels",
    "safety",
)

REQUIRED_SAFETY = (
    "sanitized",
    "contains_credentials",
    "external_network_required",
    "user_authorized_or_synthetic",
)


def load_artifact(path: Path | str) -> dict[str, Any]:
    artifact_path = Path(path)
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def discover_seed_artifacts(root: Path | str) -> list[Path]:
    root_path = Path(root)
    if not root_path.exists():
        return []
    return sorted(root_path.glob("seed_*/failure_artifact.json"))


def validate_artifact(artifact: Mapping[str, Any], base_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in artifact:
            errors.append(f"missing top-level field: {key}")

    if artifact.get("schema_version") != "failure-artifact/v1":
        errors.append("schema_version must be failure-artifact/v1")

    safety = artifact.get("safety", {})
    if not isinstance(safety, Mapping):
        errors.append("safety must be an object")
    else:
        for key in REQUIRED_SAFETY:
            if key not in safety:
                errors.append(f"missing safety field: {key}")
        if safety.get("contains_credentials") is True:
            errors.append("artifact must not contain credentials")

    labels = artifact.get("labels", {})
    if isinstance(labels, Mapping):
        if not labels.get("failure_type"):
            errors.append("labels.failure_type is required for seed artifacts")
    else:
        errors.append("labels must be an object")

    artifact_refs = artifact.get("artifacts", {})
    if base_dir and isinstance(artifact_refs, Mapping):
        for name, rel_path in artifact_refs.items():
            if rel_path in ("", None):
                continue
            if not isinstance(rel_path, str):
                errors.append(f"artifact reference {name} must be a relative path string")
                continue
            if Path(rel_path).is_absolute():
                errors.append(f"artifact reference {name} must be relative")
            if ".." in Path(rel_path).parts:
                errors.append(f"artifact reference {name} must not escape artifact directory")

    return errors
