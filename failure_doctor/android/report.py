from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_android_report(payload: dict[str, Any], out_dir: Path | str, name: str) -> dict[str, Any]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / f"{name}.json"
    md_path = output / f"{name}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(
        f"# Android Report\n\nStatus: `{payload.get('status', 'unknown')}`\n\nSchema: `{payload.get('schema_version', 'unknown')}`\n",
        encoding="utf-8",
    )
    return {"json": str(json_path), "markdown": str(md_path)}
