import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import enrich_for_users


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "public_failure_corpus" / "report_snapshots"


def run_failure_doctor(log_text: str) -> tuple[dict, str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        input_dir = root / "input"
        out_dir = root / "report"
        input_dir.mkdir()
        (input_dir / "error.log").write_text(log_text, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(out_dir)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
        report = (out_dir / "diagnosis.md").read_text(encoding="utf-8")
        prompt = (out_dir / "codex_fix_prompt.md").read_text(encoding="utf-8")
        return diagnosis, report, prompt


class FailureDoctorActionableReportTests(unittest.TestCase):
    def test_diagnosis_json_includes_actionable_v02_fields(self):
        diagnosis, _report, _prompt = run_failure_doctor("page.goto: net::ERR_PROXY_CONNECTION_FAILED")

        self.assertEqual(diagnosis["estimated_fix_difficulty"], "medium")
        self.assertIn("transport subtype hint", diagnosis["confidence_reason"])
        self.assertIn("proxy_connection_failed", diagnosis["confidence_reason"])

    def test_diagnosis_markdown_uses_human_readable_actionable_sections(self):
        _diagnosis, report, _prompt = run_failure_doctor(
            "locator.click: Error: strict mode violation: locator('button') resolved to 2 elements"
        )

        for heading in ("## 结论", "## 证据", "## 为什么", "## 下一步", "## 给 Codex 的修复指令"):
            self.assertIn(heading, report)
        self.assertIn("按钮/元素找不到", report)
        self.assertIn("为什么不是其他分类", report)

    def test_codex_fix_prompt_has_repair_levels_and_boundaries(self):
        _diagnosis, _report, prompt = run_failure_doctor("Download event fired but file was not saved; acceptDownloads is false")

        for heading in ("## 保守修复", "## 推荐修复", "## 验证命令", "## 禁止修改范围"):
            self.assertIn(heading, prompt)
        self.assertIn("不要改业务逻辑", prompt)
        self.assertIn("不要加入 Cookie、Token、Authorization 或密码", prompt)

    def test_actionable_report_outputs_do_not_contain_mojibake(self):
        diagnosis, report, prompt = run_failure_doctor("Error: Execution context was destroyed, most likely because of a navigation")
        combined = json.dumps(diagnosis, ensure_ascii=False) + report + prompt

        for marker in ("閹", "鐠", "閳", "娑", "閻", "缂"):
            self.assertNotIn(marker, combined)

    def test_estimated_fix_difficulty_easy_medium_hard_mapping(self):
        self.assertEqual(
            enrich_for_users({"failure_type": "playwright_strict_mode_violation", "confidence": 0.87})[
                "estimated_fix_difficulty"
            ],
            "easy",
        )
        self.assertEqual(
            enrich_for_users({"failure_type": "network_http_error", "subtype": "proxy_connection_failed", "confidence": 0.88})[
                "estimated_fix_difficulty"
            ],
            "medium",
        )
        self.assertEqual(
            enrich_for_users({"failure_type": "cdp_websocket_disconnected", "confidence": 0.87})[
                "estimated_fix_difficulty"
            ],
            "hard",
        )

    def test_confidence_reason_mentions_evidence_level_when_available(self):
        public = enrich_for_users(
            {
                "failure_type": "playwright_route_mock_har",
                "subtype": "har_fallback_network_leak",
                "confidence": 0.9,
                "evidence_level": "confirmed",
                "evidence": ["routeFromHAR used fallback and allowed a live network request"],
            }
        )

        self.assertIn("confirmed", public["confidence_reason"])
        self.assertIn("routeFromHAR used fallback", public["confidence_reason"])

    def test_five_corpus_report_snapshots_exist(self):
        snapshots = sorted(SNAPSHOT_DIR.glob("*.md"))
        self.assertEqual(len(snapshots), 5)

    def test_corpus_report_snapshots_have_actionable_sections(self):
        for snapshot in sorted(SNAPSHOT_DIR.glob("*.md")):
            text = snapshot.read_text(encoding="utf-8")
            for heading in ("## 结论", "## 证据", "## 为什么", "## 下一步", "## 给 Codex 的修复指令"):
                self.assertIn(heading, text, snapshot.name)
            self.assertNotIn("閹", text, snapshot.name)

    def test_readme_contains_before_after_report_example(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Before / After Report", readme)
        self.assertIn("conclusion / evidence / why / next action / Codex fix prompt", readme)


if __name__ == "__main__":
    unittest.main()
