import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DATA = ROOT / "validation" / "public_failure_validation_50.json"
VALIDATION_REPORT = ROOT / "docs" / "VALIDATION_REPORT.md"
COMMERCIAL_DOC = ROOT / "docs" / "COMMERCIAL_USE_CASES.md"


class ValidationPackTests(unittest.TestCase):
    def test_validation_dataset_has_50_unseen_public_samples(self):
        payload = json.loads(VALIDATION_DATA.read_text(encoding="utf-8"))
        cases = payload["cases"]

        self.assertEqual(len(cases), 50)
        for case in cases:
            for field in (
                "case_id",
                "source_url",
                "input_type",
                "expected_category",
                "actual_category",
                "confidence",
                "has_effective_next_action",
                "has_codex_fix_prompt",
                "is_misclassified",
            ):
                self.assertIn(field, case, case.get("case_id"))
            self.assertTrue(case["source_url"].startswith("https://"), case["case_id"])

    def test_validation_metrics_meet_targets(self):
        payload = json.loads(VALIDATION_DATA.read_text(encoding="utf-8"))
        metrics = payload["metrics"]

        self.assertEqual(metrics["sample_count"], 50)
        self.assertGreaterEqual(metrics["reasonable_classifications"], 35)
        self.assertGreaterEqual(metrics["usable_next_actions"], 40)
        self.assertLessEqual(metrics["severe_misclassifications"], 5)
        self.assertGreaterEqual(metrics["insufficient_evidence_cases"], 1)

    def test_validation_report_documents_results_and_boundaries(self):
        text = VALIDATION_REPORT.read_text(encoding="utf-8")

        for phrase in (
            "测试样本数量：150",
            "GitHub Issues / Stack Overflow / browser-use / Playwright",
            "准确分类率",
            "可执行建议率",
            "误判案例",
            "证据不足案例",
            "当前边界",
        ):
            self.assertIn(phrase, text)

    def test_commercial_use_cases_document_exists_with_boundaries(self):
        text = COMMERCIAL_DOC.read_text(encoding="utf-8")

        for phrase in (
            "AI Agent 调试助手",
            "RPA 故障排查工具",
            "Playwright/E2E 测试失败诊断",
            "企业内部自动化脚本维护工具",
            "不是 CAPTCHA 绕过",
            "不是反爬绕过",
            "不是真实平台采集器",
        ):
            self.assertIn(phrase, text)

    def test_readme_top_has_three_minimal_demos_without_mojibake(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "案例 1：代理失败 log",
            "案例 2：strict mode violation",
            "案例 3：trace.zip 登录失效",
        ):
            self.assertIn(phrase, readme)
        for marker in ("鈹", "鈫", "鎶", "璇", "涓", "鐧", "缃"):
            self.assertNotIn(marker, readme)


if __name__ == "__main__":
    unittest.main()
