from __future__ import annotations

from pathlib import Path
from typing import Any

from .loader import load_suite
from .report import write_benchmark_report
from .scoring import score_case


def run_benchmark(suite: str, out: Path) -> dict[str, Any]:
    cases = load_suite(suite)
    results = [score_case(case) for case in cases]
    return write_benchmark_report(Path(out), suite, results)
