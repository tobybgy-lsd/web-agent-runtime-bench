"""Regression corpus helper for sanitized failure packs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def add_to_corpus(src: Path | str, sanitize: bool = True) -> dict:
    src_path = Path(src)
    artifact_path = src_path / "failure_artifact.json"
    if not artifact_path.exists():
        return {"ok": False, "error": "failure_artifact.json not found"}
    case_id = src_path.name
    root = Path("failure_corpus") / ("sanitized" if sanitize else "raw")
    dst = root / case_id
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src_path, dst)
    return {"ok": True, "case_id": case_id, "corpus_path": str(dst)}


def generate_synthetic_fixture(src: Path | str, out_root: Path | str = "failure_corpus/synthetic") -> dict:
    src_path = Path(src)
    artifact_path = src_path / "failure_artifact.json"
    if not artifact_path.exists():
        return {"ok": False, "error": "failure_artifact.json not found"}

    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    case_id = _safe_case_id(str(artifact.get("run_id") or src_path.name))
    dst = Path(out_root) / case_id
    dst.mkdir(parents=True, exist_ok=True)

    shutil.copy2(artifact_path, dst / "failure_artifact.json")
    metadata = {
        "case_id": case_id,
        "failure_type": artifact.get("labels", {}).get("failure_type", "unknown"),
        "source_target_type": artifact.get("target_type", "unknown"),
        "tool": artifact.get("tool", "unknown"),
        "replay_mode": "synthetic_metadata_only",
        "safety": {
            "external_network_required": False,
            "contains_credentials": False,
            "notes": "Generated from sanitized artifact metadata. Does not replay real network calls.",
        },
        "assertions": {
            "expected_failure_type": artifact.get("labels", {}).get("failure_type", "unknown"),
            "required_evidence_present": True,
        },
    }
    (dst / "replay_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dst / "README.md").write_text(_render_fixture_readme(metadata), encoding="utf-8")
    return {"ok": True, "case_id": case_id, "fixture_path": str(dst)}


def _safe_case_id(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value.strip())
    return safe or "failure_case"


def _render_fixture_readme(metadata: dict) -> str:
    return f"""# Synthetic Failure Fixture: {metadata["case_id"]}

- Failure type: `{metadata["failure_type"]}`
- Tool: `{metadata["tool"]}`
- Replay mode: `{metadata["replay_mode"]}`

This fixture is generated from sanitized metadata. It must not require external
network access, credentials, cookies, or platform-specific bypass logic.
"""
