import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CredibilityEngineeringTests(unittest.TestCase):
    def test_pyproject_exposes_installable_failure_doctor_cli(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("[project]", pyproject)
        self.assertIn('name = "agent-failure-doctor"', pyproject)
        self.assertIn("[project.scripts]", pyproject)
        self.assertIn('failure-doctor = "failure_doctor.cli:main"', pyproject)
        self.assertIn('trace-doctor = "trace_doctor.cli:main"', pyproject)

    def test_console_script_works_after_editable_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            venv_dir = Path(tmp) / "venv"
            out_dir = Path(tmp) / "report"

            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            if sys.platform == "win32":
                python_bin = venv_dir / "Scripts" / "python.exe"
                cli_bin = venv_dir / "Scripts" / "failure-doctor.exe"
            else:
                python_bin = venv_dir / "bin" / "python"
                cli_bin = venv_dir / "bin" / "failure-doctor"

            subprocess.run(
                [str(python_bin), "-m", "pip", "install", "-e", "."],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    str(cli_bin),
                    "diagnose",
                    str(ROOT / "examples" / "failed_runs" / "proxy_failed"),
                    "--out",
                    str(out_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((out_dir / "diagnosis.json").exists())
            self.assertTrue((out_dir / "codex_fix_prompt.md").exists())

    def test_validation_150_records_are_honest_traceable_sanitized_records(self):
        data = json.loads((ROOT / "validation" / "public_failure_validation_150.json").read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], "validation-pack/v0.6-credibility")
        self.assertIn("public-inspired / sanitized validation records", data["method"])
        self.assertNotIn("42001", json.dumps(data))
        self.assertNotIn("42002", json.dumps(data))

        cases = data["cases"]
        self.assertEqual(len(cases), 150)
        for case in cases:
            for field in (
                "source_url",
                "source_title",
                "source_type",
                "retrieved_at",
                "raw_error_excerpt",
                "sanitization_note",
            ):
                self.assertIn(field, case, case.get("case_id"))
                self.assertTrue(str(case[field]).strip(), case.get("case_id"))
            self.assertTrue(case["source_url"].startswith("https://"), case["case_id"])
            self.assertNotRegex(case["source_url"], r"/issues/42\d{3}$")
            self.assertLessEqual(len(case["raw_error_excerpt"].split()), 24, case["case_id"])

    def test_archive_excludes_git_outputs_pycache_and_sample_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "source.zip"
            subprocess.run(
                ["git", "archive", "--format", "zip", f"--output={archive_path}", "HEAD"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()

            forbidden_parts = (".git/", "__pycache__/", "outputs/", "sample_run/")
            for name in names:
                self.assertFalse(any(part in name for part in forbidden_parts), name)

    def test_ci_runs_unit_tests_on_windows_linux_and_macos(self):
        workflow = (ROOT / ".github" / "workflows" / "benchmark.yml").read_text(encoding="utf-8")

        self.assertIn("unit-tests:", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("macos-latest", workflow)
        self.assertIn("benchmark-windows:", workflow)


if __name__ == "__main__":
    unittest.main()
