from __future__ import annotations

from pathlib import Path
from typing import Any

from failure_doctor.cases.models import read_json

from .models import SUPPORTED_SUITES, synthetic_case


def load_suite(suite: str | Path) -> list[dict[str, Any]]:
    value = str(suite)
    if value in SUPPORTED_SUITES:
        count = 150 if value == "public-safe" else 60
        return [synthetic_case(f"{value.replace('-', '_')}_{idx + 1:03d}", value, idx) for idx in range(count)]
    root = Path(suite)
    cases: list[dict[str, Any]] = []
    for manifest in sorted(root.rglob("case_manifest.json")):
        cases.append(read_json(manifest))
    return cases
