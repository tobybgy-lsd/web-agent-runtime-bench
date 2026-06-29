from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = ROOT / "knowledge_base"
PATTERN_DIRS = (
    "failure_patterns",
    "fix_patterns",
    "evidence_patterns",
    "framework_patterns",
    "domain_patterns",
    "regression_patterns",
)


def load_patterns(root: Path = KB_ROOT) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for dirname in PATTERN_DIRS:
        directory = root / dirname
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["_path"] = str(path.relative_to(root))
            patterns.append(payload)
    return patterns


def pattern_text(pattern: dict[str, Any]) -> str:
    return json.dumps(pattern, ensure_ascii=False, sort_keys=True).lower()


if __name__ == "__main__":
    print(json.dumps({"patterns": load_patterns()}, indent=2, ensure_ascii=False))
