import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicReleaseCleanupTests(unittest.TestCase):
    def test_gitignore_covers_common_generated_files(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in (
            "__pycache__/",
            "*.py[cod]",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            ".coverage",
            "htmlcov/",
            "outputs/",
            "sample_run/",
            "report/",
            "reports/",
            "tmp/",
            "*.tmp",
            ".venv/",
            "venv/",
            "env/",
            "node_modules/",
            ".DS_Store",
            ".vscode/",
            ".idea/",
        ):
            self.assertIn(pattern, text)

    def test_public_release_docs_exist_with_security_boundaries(self):
        required_files = (
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "CODE_OF_CONDUCT.md",
            "README.zh-CN.md",
            "validation/dashboard.md",
        )
        for rel in required_files:
            self.assertTrue((ROOT / rel).exists(), rel)

        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        for phrase in (
            "local-first",
            "does not upload artifacts",
            "passwords",
            "cookies",
            "session tokens",
            "authorization headers",
            "API keys",
            "CAPTCHA bypass",
            "bot evasion",
            "credential extraction",
            "unauthorized scraping",
            "anti-abuse circumvention",
        ):
            self.assertIn(phrase, security)

    def test_pyproject_has_public_package_metadata_without_unused_dependencies(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        for phrase in (
            'version = "0.4.0"',
            "sida lin",
            "[project.urls]",
            'Homepage = "https://github.com/tobybgy-lsd/web-agent-runtime-bench"',
            "[tool.ruff]",
            "[tool.black]",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("jsonschema", text)
        self.assertNotIn("PyYAML", text)

    def test_schema_id_uses_repository_url_not_placeholder_local(self):
        schema = json.loads((ROOT / "schemas" / "failure_artifact.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(
            schema["$id"],
            "https://github.com/tobybgy-lsd/web-agent-runtime-bench/schemas/failure_artifact.schema.json",
        )
        self.assertNotIn("example" + ".local", json.dumps(schema))

    def test_root_directory_has_no_internal_report_files(self):
        root_reports = [path.name for path in ROOT.glob("*_REPORT.md")]
        root_reports += [path.name for path in ROOT.glob("*AUDIT*.md")]
        self.assertEqual(root_reports, [])
        internal = ROOT / "docs" / "internal"
        self.assertTrue(internal.exists())
        self.assertTrue((internal / "AUDIT_REPORT.md").exists())

    def test_readme_is_english_first_with_badges_and_links(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        top = readme[:1200]
        for phrase in (
            "[中文文档](README.zh-CN.md)",
            "![CI]",
            "![License: MIT]",
            "![Python 3.10+]",
            "python -m pip install -e .",
            "failure-doctor diagnose .\\examples\\failed_runs\\proxy_network_error --out .\\report",
            "GitHub issue draft",
            "See [validation/dashboard.md](validation/dashboard.md)",
        ):
            self.assertIn(phrase, top)
        for marker in ("閳", "鏀", "娑", "閸", "缁"):
            self.assertNotIn(marker, readme)

    def test_readme_zh_cn_links_back_to_english(self):
        text = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("[English documentation](README.md)", text)
        self.assertIn("Agent Failure Doctor", text)
        self.assertIn("本地优先", text)

    def test_validation_dashboard_contains_current_honest_metrics(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        for phrase in (
            "# Validation Dashboard",
            "| v0.4.0 | 150 | 97.3% | 94.7% | 4 | 21 | 170 |",
            "public-inspired sanitized validation records",
            "not full real-world failure packages",
        ):
            self.assertIn(phrase, text)

    def test_no_tracked_runtime_garbage_or_placeholder_local_remains(self):
        tracked = (ROOT / "validation" / "public_failure_validation_150.json").read_text(encoding="utf-8")
        self.assertNotRegex(tracked, re.compile(r"https://github.com/.+/issues/42\d{3}"))


if __name__ == "__main__":
    unittest.main()
