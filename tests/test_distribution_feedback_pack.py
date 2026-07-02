import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DistributionFeedbackPackTests(unittest.TestCase):
    def test_pyproject_is_pypi_ready(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn('name = "agent-failure-doctor"', pyproject)
        self.assertIn('version = "3.9.0"', pyproject)
        self.assertIn('"Development Status :: 4 - Beta"', pyproject)
        self.assertIn('failure-doctor = "failure_doctor.cli:main"', pyproject)
        self.assertIn('Repository = "https://github.com/tobybgy-lsd/web-agent-runtime-bench"', pyproject)

    def test_pypi_release_runbook_exists(self):
        doc = (ROOT / "docs" / "PYPI_RELEASE.md").read_text(encoding="utf-8")

        self.assertIn("pip install agent-failure-doctor", doc)
        self.assertIn("python -m build", doc)
        self.assertIn("python -m twine check dist/*", doc)
        self.assertIn("twine upload dist/*", doc)
        self.assertIn("Trusted Publishing", doc)
        self.assertIn("Do not commit PyPI tokens", doc)

    def test_manual_pypi_publish_workflow_exists(self):
        workflow = (ROOT / ".github" / "workflows" / "publish-pypi.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("workflow_dispatch", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("python -m build", workflow)
        self.assertIn("pypa/gh-action-pypi-publish", workflow)

    def test_demo_and_article_assets_exist(self):
        demo = (ROOT / "docs" / "DEMO_VIDEO_SCRIPT.md").read_text(encoding="utf-8")
        article = (ROOT / "docs" / "TECH_ARTICLE_DRAFT.md").read_text(encoding="utf-8")

        for phrase in (
            "2-minute demo",
            "failure-doctor collect",
            "diagnosis.md",
            "ai_handoff",
            "failure-doctor verify",
        ):
            self.assertIn(phrase, demo)

        for phrase in (
            "From Automation Failure Logs to AI Repair Task Packs",
            "Auto Collector",
            "Evidence-based Diagnosis",
            "AI Handoff",
            "Safety Boundary",
            "P98 Gate",
        ):
            self.assertIn(phrase, article)

    def test_real_feedback_loop_is_documented(self):
        doc = (ROOT / "docs" / "REAL_USER_FEEDBACK_LOOP.md").read_text(encoding="utf-8")

        self.assertIn("5 real sanitized failure cases", doc)
        self.assertIn("external_failure_case.yml", doc)
        self.assertIn("first-run before rule changes", doc)
        self.assertIn("do not count synthetic examples", doc)
        self.assertIn("EXT-YYYY-NNNN", doc)


if __name__ == "__main__":
    unittest.main()
