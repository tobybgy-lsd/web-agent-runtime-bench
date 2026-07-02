from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compare import compare_benchmarks
from .runner import run_benchmark
from .validation import validate_suite


def add_benchmark_parser(sub: argparse._SubParsersAction) -> None:
    benchmark = sub.add_parser("benchmark", help="Run public-safe local benchmark suites")
    bench_sub = benchmark.add_subparsers(dest="benchmark_command")
    run = bench_sub.add_parser("run", help="Run a public-safe or regression benchmark")
    run.add_argument("--suite", required=True)
    run.add_argument("--out", required=True)
    compare = bench_sub.add_parser("compare", help="Compare two benchmark reports")
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--out", required=True)
    validate = bench_sub.add_parser("validate-suite", help="Validate a public benchmark suite")
    validate.add_argument("--suite", required=True)
    validate.add_argument("--out", default=None)


def handle_benchmark(args: argparse.Namespace) -> int:
    command = getattr(args, "benchmark_command", None)
    try:
        if command == "run":
            result = run_benchmark(str(args.suite), Path(args.out))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if command == "compare":
            result = compare_benchmarks(Path(args.baseline), Path(args.candidate), Path(args.out))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["regression_compare_pass"] else 3
        if command == "validate-suite":
            result = validate_suite(str(args.suite), Path(args.out) if args.out else None)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 3
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("unknown benchmark command")
    return 2
