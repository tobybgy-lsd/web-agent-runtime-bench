import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_150 = ROOT / "validation" / "public_failure_validation_150.json"
VALIDATION_REPORT = ROOT / "docs" / "VALIDATION_REPORT.md"
CORPUS_CASES = ROOT / "public_failure_corpus" / "cases"
REGRESSION_SNAPSHOTS = ROOT / "public_failure_corpus" / "regression_snapshots"


class HardeningPackTests(unittest.TestCase):
    def test_validation_150_dataset_meets_v05_targets(self):
        payload = json.loads(VALIDATION_150.read_text(encoding="utf-8"))
        metrics = payload["metrics"]

        self.assertEqual(metrics["sample_count"], 150)
        self.assertGreaterEqual(metrics["reasonable_classifications"], 128)
        self.assertGreaterEqual(metrics["usable_next_actions"], 135)
        self.assertLessEqual(metrics["severe_misclassifications"], 5)
        self.assertGreaterEqual(metrics["insufficient_evidence_cases"], 15)

    def test_validation_150_cases_have_required_fields(self):
        payload = json.loads(VALIDATION_150.read_text(encoding="utf-8"))
        cases = payload["cases"]

        self.assertEqual(len(cases), 150)
        required = {
            "case_id",
            "source_url",
            "source_title",
            "source_type",
            "retrieved_at",
            "raw_error_excerpt",
            "input_type",
            "expected_category",
            "actual_category",
            "confidence",
            "has_effective_next_action",
            "has_codex_fix_prompt",
            "is_misclassified",
            "evidence_level",
            "sanitization_note",
        }
        for case in cases:
            self.assertTrue(required.issubset(case), case.get("case_id"))
            self.assertTrue(case["source_url"].startswith("https://"), case["case_id"])

    def test_public_failure_corpus_has_150_cases(self):
        case_count = 0
        for path in CORPUS_CASES.glob("*.yaml"):
            case_count += path.read_text(encoding="utf-8").count("case_id:")
        self.assertGreaterEqual(case_count, 150)

    def test_regression_snapshots_lock_typical_misclassifications(self):
        snapshots = sorted(REGRESSION_SNAPSHOTS.glob("*.md"))
        self.assertGreaterEqual(len(snapshots), 8)
        text = "\n".join(path.read_text(encoding="utf-8") for path in snapshots)

        for phrase in (
            "Docker / headless",
            "browser executable missing",
            "Chromium sandbox",
            "download path / permission",
            "iframe / frame detached",
            "worker / service worker cache",
            "memory crash / target closed",
            "agent loop / repeated action",
        ):
            self.assertIn(phrase, text)

    def test_validation_report_is_updated_to_150_traceable_records(self):
        text = VALIDATION_REPORT.read_text(encoding="utf-8")

        self.assertIn("测试样本数量：150", text)
        self.assertIn("public-inspired / sanitized validation records", text)
        self.assertIn("合理分类数：146", text)
        self.assertIn("可执行建议数：142", text)
        self.assertIn("严重误判：4", text)
        self.assertIn("证据不足案例：21", text)


def _make_validation_case_test(index: int):
    def test(self):
        payload = json.loads(VALIDATION_150.read_text(encoding="utf-8"))
        case = payload["cases"][index]
        self.assertTrue(case["has_codex_fix_prompt"], case["case_id"])
        if case["actual_category"] == "insufficient_evidence":
            self.assertEqual(case["evidence_level"], "low", case["case_id"])
        else:
            self.assertGreaterEqual(float(case["confidence"]), 0.7, case["case_id"])

    return test


for _index in range(40):
    setattr(HardeningPackTests, f"test_validation_case_{_index + 1:03d}_prompt_and_confidence", _make_validation_case_test(_index))


if __name__ == "__main__":
    unittest.main()
