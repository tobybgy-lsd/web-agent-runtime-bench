from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "failure_doctor", *args],
        cwd=str(cwd or ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_report(
    root: Path,
    name: str,
    *,
    failure_type: str = "playwright_locator",
    subtype: str = "selector_timeout",
    summary: str = "selector timeout after login redirect",
    safe: bool = True,
    next_action: str = "Check the selector and authenticated page state.",
) -> Path:
    report = root / name
    report.mkdir(parents=True)
    diagnosis = {
        "user_facing_category": "按钮/元素找不到",
        "technical_category": failure_type,
        "failure_type": failure_type,
        "subtype": subtype,
        "confidence": 0.86,
        "next_action": next_action,
        "raw_diagnosis": {
            "failure_type": failure_type,
            "subtype": subtype,
            "confidence": 0.86,
            "observations": {"error_signature": summary},
        },
    }
    if not safe:
        diagnosis["next_action"] = "captcha bypass private solver FLAG{do_not_store}"
        diagnosis["raw_diagnosis"]["observations"]["private_solution"] = "private_solutions"
    (report / "diagnosis.json").write_text(json.dumps(diagnosis, indent=2), encoding="utf-8")
    (report / "diagnosis.md").write_text(f"# Diagnosis\n\n{summary}\n", encoding="utf-8")
    (report / "evidence.json").write_text(
        json.dumps({"artifact": {"observations": {"error_signature": summary}}}, indent=2),
        encoding="utf-8",
    )
    (report / "repair_suggestions.md").write_text(next_action, encoding="utf-8")
    return report


class LocalFailureKnowledgeBaseCliTests(unittest.TestCase):
    def test_kb_help_and_init_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / ".failure-doctor-kb"

            help_result = run_cli("kb", "--help")
            self.assertEqual(help_result.returncode, 0, help_result.stderr + help_result.stdout)
            self.assertIn("init", help_result.stdout)

            init_result = run_cli("kb", "init", "--path", str(kb))
            self.assertEqual(init_result.returncode, 0, init_result.stderr + init_result.stdout)
            manifest = json.loads((kb / "kb_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "failure_kb/v1")
            self.assertTrue(manifest["local_only"])
            self.assertTrue(manifest["sanitized_only"])

            status_result = run_cli("kb", "status", "--kb", str(kb))
            self.assertEqual(status_result.returncode, 0, status_result.stderr + status_result.stdout)
            self.assertTrue((kb / "kb_health_report.json").exists())

    def test_safe_import_match_promote_and_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "kb"
            report = write_report(root, "safe_report")
            current = write_report(
                root,
                "current_report",
                summary="selector timeout after login redirect on submit button",
            )
            verification = root / "verification"
            verification.mkdir()
            (verification / "verification_report.json").write_text(
                json.dumps(
                    {
                        "status": "resolved",
                        "validation_commands": ["python -m pytest tests/test_login.py"],
                        "fix_summary": "Wait for authenticated redirect before clicking the submit button.",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            self.assertEqual(run_cli("kb", "init", "--path", str(kb)).returncode, 0)
            imported = run_cli("kb", "import-report", "--kb", str(kb), "--report", str(report))
            self.assertEqual(imported.returncode, 0, imported.stderr + imported.stdout)

            case_list = json.loads((kb / "indexes" / "case_index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(case_list["cases"]), 1)
            case_id = case_list["cases"][0]["case_id"]

            search = run_cli("kb", "search", "--kb", str(kb), "--query", "selector timeout login redirect")
            self.assertEqual(search.returncode, 0, search.stderr + search.stdout)
            self.assertIn(case_id, search.stdout)

            match_out = root / "match"
            match = run_cli("kb", "match", "--kb", str(kb), "--report", str(current), "--out", str(match_out))
            self.assertEqual(match.returncode, 0, match.stderr + match.stdout)
            matches = json.loads((match_out / "similar_cases.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(matches["matches"][0]["score"], 0.5)

            promoted = run_cli(
                "kb",
                "promote-fix",
                "--kb",
                str(kb),
                "--case-id",
                case_id,
                "--verification",
                str(verification),
            )
            self.assertEqual(promoted.returncode, 0, promoted.stderr + promoted.stdout)
            case = json.loads((kb / "cases" / case_id / "case.json").read_text(encoding="utf-8"))
            self.assertEqual(case["fix_status"], "verified")
            self.assertTrue(case["verified_fix"]["do_not_apply_automatically"])

            export = root / "export"
            exported = run_cli("kb", "export", "--kb", str(kb), "--out", str(export), "--sanitized-only")
            self.assertEqual(exported.returncode, 0, exported.stderr + exported.stdout)
            exported_text = (export / "cases.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("FLAG{", exported_text)
            self.assertNotIn("private_solutions", exported_text)

    def test_blocked_report_is_not_imported_or_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "kb"
            blocked_report = write_report(root, "blocked_report", safe=False)
            verification = root / "verification"
            verification.mkdir()
            (verification / "verification_report.json").write_text(
                json.dumps({"status": "resolved", "fix_summary": "unsafe bypass"}, indent=2),
                encoding="utf-8",
            )
            self.assertEqual(run_cli("kb", "init", "--path", str(kb)).returncode, 0)
            blocked = run_cli("kb", "import-report", "--kb", str(kb), "--report", str(blocked_report))
            self.assertNotEqual(blocked.returncode, 0)
            manifest = json.loads((kb / "kb_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["case_count"], 0)

    def test_diagnose_with_kb_writes_similar_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "kb"
            historical = write_report(root, "historical", subtype="proxy_connection_failed", summary="ERR_PROXY_CONNECTION_FAILED")
            failed = root / "failed"
            failed.mkdir()
            (failed / "error.log").write_text("net::ERR_PROXY_CONNECTION_FAILED while opening page\n", encoding="utf-8")
            out = root / "report"

            self.assertEqual(run_cli("kb", "init", "--path", str(kb)).returncode, 0)
            self.assertEqual(run_cli("kb", "import-report", "--kb", str(kb), "--report", str(historical)).returncode, 0)
            diagnosed = run_cli("diagnose", str(failed), "--kb", str(kb), "--out", str(out))
            self.assertEqual(diagnosed.returncode, 0, diagnosed.stderr + diagnosed.stdout)
            self.assertTrue((out / "similar_cases.json").exists())
            self.assertTrue((out / "kb_recommendations.md").exists())


if __name__ == "__main__":
    unittest.main()

