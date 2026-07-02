import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class AutoCollectorSafetyTests(unittest.TestCase):
    def test_collect_cli_rejects_missing_project_and_forbidden_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "collect", "--project", str(Path(tmp) / "missing"), "--out", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("project not found", result.stdout + result.stderr)

    def test_collect_cli_generates_safe_next_action_not_bypass_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "error.log").write_text("HTTP 429 captcha verify you are human\n", encoding="utf-8")
            out = Path(tmp) / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "collect",
                    "--project",
                    str(root),
                    "--preset",
                    "auto",
                    "--out",
                    str(out),
                    "--auto-diagnose",
                    "--auto-handoff",
                    "--auto-sanitize",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, (result.stdout or "") + (result.stderr or ""))
            combined = "\n".join(
                path.read_text(encoding="utf-8", errors="replace").lower()
                for path in out.rglob("*")
                if path.is_file() and path.suffix.lower() in {".md", ".json", ".log", ".txt"}
            )
            for forbidden in ("bypass cloudflare", "閻袙", "缂佹洝绻冩搴㈠付", "鏉╁洭鐛欑拠浣虹垳"):
                self.assertNotIn(forbidden, combined)


