from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from failure_doctor.visual_runtime.adapter import adapt_visual_artifacts
from failure_doctor.visual_runtime.compare import compare_visual_runs
from failure_doctor.visual_runtime.loader import load_visual_run
from failure_doctor.visual_runtime.mock_vlm import call_vlm_api, mock_vlm_observe
from failure_doctor.visual_runtime.report import write_visual_runtime_report
from tools.validation.run_visual_agent_runtime_validation import CASES_ROOT, ensure_cases


class VisualRuntimeCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_cases()

    def test_pure_visual_no_dom_degrades_without_dom(self) -> None:
        case = CASES_ROOT / "pure_visual_insufficient_evidence_001" / "visual_run"
        with tempfile.TemporaryDirectory() as tmp:
            report = write_visual_runtime_report(case, Path(tmp), no_dom=True)
            self.assertEqual(report["diagnosis"]["subtype"], "pure_visual_insufficient_evidence")

    def test_safety_sensitive_visual_run_blocks_when_requested(self) -> None:
        case = CASES_ROOT / "visual_runtime_safety_blocked_001" / "visual_run"
        with tempfile.TemporaryDirectory() as tmp:
            report = write_visual_runtime_report(case, Path(tmp), dom_optional=True, safety_evaluate=True)
            self.assertEqual(report["diagnosis"]["subtype"], "visual_runtime_safety_blocked")
            self.assertEqual(report["diagnosis"]["screenshot_upload_count"], 0)

    def test_compare_reports_recommendation(self) -> None:
        baseline = CASES_ROOT / "coordinate_click_drift_001" / "visual_run"
        candidate = CASES_ROOT / "dpr_scaling_mismatch_001" / "visual_run"
        with tempfile.TemporaryDirectory() as tmp:
            report = compare_visual_runs(baseline, candidate, Path(tmp))
            self.assertIn("recommendation", report)
            self.assertTrue((Path(tmp) / "latency_comparison.csv").exists())

    def test_adapter_creates_local_visual_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            out = Path(tmp) / "out"
            src.mkdir()
            summary = adapt_visual_artifacts("generic", src, out)
            self.assertEqual(summary["external_vlm_call_count"], 0)
            self.assertTrue((out / "run_manifest.json").exists())
            self.assertEqual(load_visual_run(out, dom_optional=True).manifest["local_only"], True)

    def test_mock_vlm_is_offline(self) -> None:
        case = CASES_ROOT / "visual_element_misidentification_001" / "visual_run"
        self.assertGreaterEqual(len(mock_vlm_observe(case)), 1)
        disabled = call_vlm_api(case, provider="openai")
        self.assertEqual(disabled["status"], "disabled")
        self.assertEqual(disabled["external_vlm_call_count"], 0)


if __name__ == "__main__":
    unittest.main()

