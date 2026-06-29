import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
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
            'version = "3.2.0"',
            "sida lin",
            "[project.urls]",
            'Homepage = "https://github.com/tobybgy-lsd/web-agent-runtime-bench"',
            "[project.optional-dependencies]",
            'trace-gen = ["playwright>=1.45"]',
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
        top = readme[:1600]
        for phrase in (
            "[中文文档](README.zh-CN.md)",
            "![CI]",
            "![License: MIT]",
            "![Python 3.10+]",
            "Local-first failure diagnosis",
            "python -m pip install -e .",
            "failure-doctor diagnose .\\examples\\failed_runs\\proxy_network_error --out .\\report",
            "GitHub issue draft",
            "See [validation/dashboard.md](validation/dashboard.md)",
        ):
            self.assertIn(phrase, top)
        for marker in ("闂", "闁", "婵", "缂", "娑"):
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
            "## 1. Current Stable Release",
            "## 2. P95 Completed Gates",
            "## 3. P98 Master Gate",
            "| Knowledge Base P98 | 210 | 210 public-safe local synthetic patterns, schema valid | 0 | pass |",
            "| P98 Master Gate | 12 pillars | `overall_status=pass`, controlled maturity score 98 | 0 | pass |",
            "validation/p98_master_gate.json",
            "Ecosystem maturity is excluded",
        ):
            self.assertIn(phrase, text)

    def test_no_tracked_runtime_garbage_or_placeholder_local_remains(self):
        tracked = (ROOT / "validation" / "public_failure_validation_150.json").read_text(encoding="utf-8")
        self.assertNotRegex(tracked, re.compile(r"https://github.com/.+/issues/42\d{3}"))

    def test_only_failure_case_issue_templates_are_public(self):
        issue_templates = sorted(path.name for path in (ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))
        self.assertEqual(issue_templates, ["external_failure_case.yml", "failure_case.yml"])

    def test_gitattributes_sets_release_archive_and_line_endings(self):
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        for phrase in (
            ".github/ export-ignore",
            "outputs/ export-ignore",
            "sample_run/ export-ignore",
            "**/__pycache__/ export-ignore",
            "*.pyc export-ignore",
            "* text=auto eol=lf",
            "*.ps1 text eol=crlf",
            "*.bat text eol=crlf",
            "*.cmd text eol=crlf",
        ):
            self.assertIn(phrase, text)

    def test_safety_boundary_does_not_duplicate_forbidden_items(self):
        text = (ROOT / "docs" / "safety_boundary.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("Unauthorized data extraction from any platform"), 1)

    def test_release_archive_script_excludes_runtime_and_git_artifacts(self):
        forbidden = (
            ".git/",
            "outputs/",
            "sample_run/",
            "report/",
            "__pycache__/",
            ".pyc",
            "agent_failure_doctor.egg-info/",
        )
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "AgentFailureDoctor-test-source.zip"
            result = subprocess.run(
                [sys.executable, "scripts/make_release_archive.py", "--out", str(archive)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(archive) as zf:
                names = zf.namelist()
            for name in names:
                self.assertFalse(any(marker in name for marker in forbidden), name)


if __name__ == "__main__":
    unittest.main()
