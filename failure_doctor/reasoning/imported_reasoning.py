from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("provider", "imported_reasoning")
    payload.setdefault("external_api_call_count", 0)
    payload.setdefault("model_download_count", 0)
    return payload
