from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.benchmark.compare import compare_benchmarks
from failure_doctor.benchmark.runner import run_benchmark
from failure_doctor.cases.intake import create_public_case
from failure_doctor.cases.issue_pack import create_issue_pack, validate_issue_pack
from failure_doctor.cases.publish_check import publish_check_case
from failure_doctor.cases.validation import validate_case


ROOT = Path(__file__).resolve().parents[1]


class V43CaseBenchmarkProgramTests(unittest.TestCase):
    def test_case_intake_publish_check_and_issue_pack_are_public_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw_failure"
            raw.mkdir()
            (raw / "error.log").write_text(
                "TimeoutError on public-safe synthetic login form\n"
                "Authorization: Bearer secret-token\n"
                "email=test@example.com\n",
                encoding="utf-8",
            )

            case_dir = root / "case"
            created = create_public_case(raw, case_dir)
            validation = validate_case(case_dir)
            publish = publish_check_case(case_dir)
            issue = create_issue_pack(raw, root / "issue_pack")
            issue_validation = validate_issue_pack(root / "issue_pack")

            self.assertEqual(created["validation"]["status"], "pass")
            self.assertEqual(validation["status"], "pass")
            self.assertEqual(publish["status"], "pass")
            self.assertEqual(issue["validation"]["status"], "pass")
            self.assertEqual(issue_validation["status"], "pass")
            public_text = "\n".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in list(case_dir.rglob("*")) + list((root / "issue_pack").rglob("*"))
                if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".log"}
            )
            self.assertNotIn("secret-token", public_text)
            self.assertNotIn("test@example.com", public_text)

    def test_cli_exposes_case_issue_pack_and_benchmark_commands(self) -> None:
        for command in ("case", "issue-pack", "benchmark"):
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", command, "--help"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_benchmark_runner_compare_and_validations_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public_report = root / "public"
            regression_report = root / "regression"
            diff_report = root / "diff"
            public_summary = run_benchmark("public-safe", public_report)
            regression_summary = run_benchmark("regression", regression_report)
            diff = compare_benchmarks(public_report, public_report, diff_report)

            self.assertEqual(public_summary["status"], "pass")
            self.assertEqual(public_summary["total_cases"], 150)
            self.assertEqual(regression_summary["status"], "pass")
            self.assertEqual(regression_summary["total_cases"], 60)
            self.assertTrue(diff["regression_compare_pass"])
            for name in (
                "benchmark_manifest.json",
                "benchmark_summary.md",
                "benchmark_summary.json",
                "case_results.jsonl",
                "failures.md",
                "regression_diff.json",
                "open_this_first_benchmark.md",
            ):
                self.assertTrue((public_report / name).exists(), name)

    def test_v43_validation_runners_feed_p98_master_gate(self) -> None:
        for module in (
            "tools.validation.run_real_user_case_program_validation",
            "tools.validation.run_public_benchmark_pack_validation",
            "tools.validation.run_p98_master_gate",
        ):
            result = subprocess.run([sys.executable, "-m", module], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        gate = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["version"], "v5.2.0")
        self.assertEqual(gate["current_stable_line"], "v5.2.0")
        self.assertEqual(gate["previous_stable_line"], "v5.1.0")
        self.assertEqual(gate["pillars"]["real_user_case_program"]["status"], "pass")
        self.assertEqual(gate["pillars"]["public_benchmark_pack"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
