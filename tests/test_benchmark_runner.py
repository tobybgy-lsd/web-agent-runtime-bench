import json
import tempfile
import unittest
from pathlib import Path

from tools.benchmark.run_benchmark import (
    BenchmarkPaths,
    build_benchmark_report,
    render_markdown_report,
    select_powershell,
    write_reports,
)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_build_benchmark_report_includes_tasks_baselines_and_scenario_map(self):
        task_summaries = {
            "signed_mock_api": {
                "overall_status": "PASS",
                "signed_cases": 6,
                "verified_cases": 6,
                "negative_cases": 6,
                "negative_rejected": 6,
                "external_network": 0,
                "synthetic_only": True,
            },
            "safety_guard": {
                "overall_status": "PASS",
                "external_network": 0,
                "synthetic_only": True,
                "forbidden_real_platform": 0,
            },
        }

        report = build_benchmark_report(task_summaries)

        self.assertEqual(report["benchmark_version"], "2026-06-25")
        self.assertIn("score_summary", report)
        self.assertIn("baselines", report)
        self.assertIn("real_world_scenario_mapping", report)
        self.assertEqual(report["tasks"][0]["task_id"], "static_extraction")
        self.assertEqual(report["safety_boundary"]["external_network_allowed"], False)

    def test_render_markdown_report_contains_reproduction_command_and_scores(self):
        report = build_benchmark_report(
            {
                "safety_guard": {
                    "overall_status": "PASS",
                    "external_network": 0,
                    "synthetic_only": True,
                    "forbidden_real_platform": 0,
                }
            }
        )

        markdown = render_markdown_report(report)

        self.assertIn("# WebAgentRuntimeBench Benchmark Report", markdown)
        self.assertIn("python tools\\benchmark\\run_benchmark.py", markdown)
        self.assertIn("| Task | Status | Score |", markdown)

    def test_write_reports_creates_json_and_markdown_files(self):
        report = build_benchmark_report({})
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_reports(report, BenchmarkPaths(out_dir=Path(tmp)))

            self.assertTrue(paths.json_path.exists())
            self.assertTrue(paths.markdown_path.exists())
            data = json.loads(paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(data["benchmark_version"], "2026-06-25")

    def test_select_powershell_prefers_pwsh_then_windows_powershell(self):
        self.assertEqual(select_powershell(lambda name: name == "pwsh"), "pwsh")
        self.assertEqual(select_powershell(lambda name: name == "powershell"), "powershell")


if __name__ == "__main__":
    unittest.main()
