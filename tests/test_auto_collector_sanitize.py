import tempfile
import unittest
from pathlib import Path

from failure_doctor.auto_collect import collect_project


class AutoCollectorSanitizeTests(unittest.TestCase):
    def test_sanitized_pack_does_not_contain_raw_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            secret = "Authorization: Bearer sk-live-secret-token-1234567890"
            (root / "error.log").write_text(f"{secret}\nHTTP 401\n", encoding="utf-8")
            out = Path(tmp) / "out"

            collect_project(root, out, preset="auto", auto_sanitize=True)

            combined = "\n".join(
                path.read_text(encoding="utf-8", errors="replace")
                for path in (out / "sanitized_failure_pack").rglob("*")
                if path.is_file() and path.suffix.lower() in {".log", ".json", ".md", ".txt"}
            )
            self.assertNotIn("sk-live-secret-token-1234567890", combined)
            self.assertIn("REDACTED", combined)

    def test_does_not_collect_browser_profile_or_ssh_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "Default").mkdir()
            (root / "Default" / "Cookies").write_text("sessionid=secret", encoding="utf-8")
            (root / ".ssh").mkdir()
            (root / ".ssh" / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
            (root / "error.log").write_text("TimeoutError\n", encoding="utf-8")
            out = Path(tmp) / "out"

            manifest = collect_project(root, out, preset="auto")

            copied = " ".join(item["relative_path"] for item in manifest["files"] if item["included"])
            self.assertNotIn("Cookies", copied)
            self.assertNotIn("id_rsa", copied)
            self.assertIn("browser_profile", " ".join(item["reason"] for item in manifest["skipped_files"]))


