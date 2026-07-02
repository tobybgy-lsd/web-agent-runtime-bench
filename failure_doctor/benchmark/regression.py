from __future__ import annotations

from pathlib import Path

from .compare import compare_benchmarks


def regression_compare(baseline: Path, candidate: Path, out: Path) -> dict:
    return compare_benchmarks(baseline, candidate, out)
