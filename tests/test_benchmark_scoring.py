import unittest

from tools.benchmark.scoring import ScoreWeights, evaluate_task, summarize_scores
from tools.benchmark.standard_tasks import STANDARD_TASKS, get_task


class BenchmarkScoringTests(unittest.TestCase):
    def test_standard_task_suite_has_six_named_public_safe_tasks(self):
        task_ids = [task.task_id for task in STANDARD_TASKS]

        self.assertEqual(
            task_ids,
            [
                "static_extraction",
                "dynamic_runtime_missing",
                "bundle_shim_repair",
                "signed_mock_api",
                "failure_diagnosis",
                "safety_guard",
            ],
        )
        self.assertTrue(all(task.synthetic_only for task in STANDARD_TASKS))
        self.assertTrue(all(task.external_network_allowed is False for task in STANDARD_TASKS))

    def test_get_task_returns_task_metadata_with_user_scenario(self):
        task = get_task("signed_mock_api")

        self.assertEqual(task.task_id, "signed_mock_api")
        self.assertIn("API", task.user_scenario)
        self.assertIn("signed", task.required_capabilities)

    def test_evaluate_task_scores_only_enabled_dimensions(self):
        task = get_task("signed_mock_api")
        summary = {
            "overall_status": "PASS",
            "signed_cases": 6,
            "verified_cases": 6,
            "negative_cases": 6,
            "negative_rejected": 6,
            "external_network": 0,
            "synthetic_only": True,
        }

        result = evaluate_task(task, summary)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["dimensions"]["negative_rejection"], 1.0)
        self.assertNotIn("repair_success", result["dimensions"])

    def test_evaluate_task_penalizes_network_and_missing_negative_rejection(self):
        task = get_task("signed_mock_api")
        summary = {
            "overall_status": "PASS",
            "signed_cases": 6,
            "verified_cases": 6,
            "negative_cases": 6,
            "negative_rejected": 5,
            "external_network": 1,
            "synthetic_only": True,
        }

        result = evaluate_task(task, summary)

        self.assertEqual(result["status"], "FAIL")
        self.assertLess(result["score"], 100.0)
        self.assertEqual(result["dimensions"]["safety_guard"], 0.0)

    def test_summarize_scores_reports_overall_score_and_pass_count(self):
        results = [
            {"task_id": "a", "score": 100.0, "status": "PASS"},
            {"task_id": "b", "score": 50.0, "status": "FAIL"},
        ]

        summary = summarize_scores(results, ScoreWeights())

        self.assertEqual(summary["task_count"], 2)
        self.assertEqual(summary["passed_tasks"], 1)
        self.assertEqual(summary["overall_score"], 75.0)
        self.assertEqual(summary["overall_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()

