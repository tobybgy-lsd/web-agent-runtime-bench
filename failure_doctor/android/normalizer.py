from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .diagnosis import diagnose_android_pack


def normalize_android_input(input_dir: Path | str, out_dir: Path | str) -> dict[str, Any]:
    source = Path(input_dir)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = []
    if source.exists():
        paths = [source] if source.is_file() else sorted(path for path in source.rglob("*") if path.is_file())
        for path in paths:
            rel = path.name if source.is_file() else str(path.relative_to(source))
            files.append({"path": rel, "bytes": path.stat().st_size})
    diagnosis = diagnose_android_pack(source)
    payload = {
        "schema_version": "android_normalized_pack/v1",
        "source": str(source),
        "files": files,
        "candidate_subtype": diagnosis.get("subtype"),
        "adapter": "android-apk",
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "real_platform_access_count": 0,
    }
    (output / "android_normalized.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "adapter_manifest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
