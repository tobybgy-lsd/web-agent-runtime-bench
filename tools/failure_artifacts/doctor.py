"""Health checks for editable failure pack directories."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .classifier import classify_failure_artifact
from .schema import load_artifact, validate_artifact


def inspect_failure_pack(pack_dir: Path | str) -> dict[str, Any]:
    root = Path(pack_dir)
    checks: list[dict[str, str]] = []
    next_steps: list[str] = []

    if not root.exists():
        return _result(False, checks, None, [f"pack directory not found: {root}"], ["create or copy a failure pack directory"])
    if not root.is_dir():
        return _result(False, checks, None, [f"pack path is not a directory: {root}"], ["pass a directory, not a file"])

    artifact_path = root / "failure_artifact.json"
    if not artifact_path.exists():
        return _result(
            False,
            checks,
            None,
            ["missing failure_artifact.json"],
            ["run `warb template copy <name> --out <dir>` or `warb pack --input <raw_dir> --out <dir>`"],
        )

    schema_errors = validate_artifact(artifact_path)
    if schema_errors:
        checks.append(_check("schema", "fail", f"{len(schema_errors)} schema issue(s)"))
    else:
        checks.append(_check("schema", "pass", "failure_artifact.json is valid"))

    artifact = load_artifact(artifact_path)
    reference_errors = _missing_reference_errors(artifact, root)
    if reference_errors:
        checks.append(_check("referenced files", "fail", f"{len(reference_errors)} missing reference(s)"))
    else:
        checks.append(_check("referenced files", "pass", "all artifact references are present"))

    safety_errors = _safety_errors(artifact)
    if safety_errors:
        checks.append(_check("safety", "fail", f"{len(safety_errors)} safety issue(s)"))
    else:
        checks.append(_check("safety", "pass", "sanitized and local-only flags are set"))

    diagnosis = classify_failure_artifact(artifact)
    confidence = float(diagnosis.get("confidence", 0))
    if diagnosis.get("failure_type") == "unknown" or confidence < 0.5:
        checks.append(_check("diagnosis", "warn", "diagnosis is low-confidence or unknown"))
        next_steps.append("add more evidence such as snapshot.html, console.log, network.json, or actual_output.json")
    else:
        checks.append(_check("diagnosis", "pass", f"{diagnosis.get('failure_type')} ({confidence:.0%})"))
        next_steps.append("run `warb diagnose <pack>\\failure_artifact.json --out-dir <pack>\\diagnosis`")

    evidence_count = len(diagnosis.get("evidence", [])) if isinstance(diagnosis.get("evidence", []), list) else 0
    if evidence_count:
        checks.append(_check("evidence", "pass", f"{evidence_count} evidence item(s) extracted"))
    else:
        checks.append(_check("evidence", "warn", "no classifier evidence extracted"))
        next_steps.append("add notes.md or logs with the exact failure symptom")

    errors = schema_errors + reference_errors + safety_errors
    ready = not errors
    if ready:
        next_steps.append("review the copied files before sharing")

    return _result(ready, checks, diagnosis, errors, _unique(next_steps))


def _result(
    ready: bool,
    checks: list[dict[str, str]],
    diagnosis: Mapping[str, Any] | None,
    errors: list[str],
    next_steps: list[str],
) -> dict[str, Any]:
    return {
        "ready": ready,
        "checks": checks,
        "diagnosis": dict(diagnosis or {}),
        "errors": errors,
        "next_steps": next_steps,
    }


def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _missing_reference_errors(artifact: Mapping[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    refs = artifact.get("artifacts", {})
    if not isinstance(refs, Mapping):
        return ["artifacts must be an object"]
    for rel_path in refs.values():
        if not rel_path:
            continue
        if not isinstance(rel_path, str):
            continue
        if not (root / rel_path).exists():
            errors.append(f"missing referenced file: {rel_path}")
    return errors


def _safety_errors(artifact: Mapping[str, Any]) -> list[str]:
    safety = artifact.get("safety", {})
    if not isinstance(safety, Mapping):
        return ["safety must be an object"]
    errors: list[str] = []
    if safety.get("sanitized") is not True:
        errors.append("safety.sanitized must be true")
    if safety.get("contains_credentials") is not False:
        errors.append("safety.contains_credentials must be false")
    if safety.get("external_network_required") is not False:
        errors.append("safety.external_network_required must be false")
    if safety.get("user_authorized_or_synthetic") is not True:
        errors.append("safety.user_authorized_or_synthetic must be true")
    return errors


def _unique(items: list[str]) -> list[str]:
    seen = set()
    unique_items = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique_items.append(item)
    return unique_items
