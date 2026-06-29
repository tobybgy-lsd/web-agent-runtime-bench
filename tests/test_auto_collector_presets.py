import tempfile
import unittest
from pathlib import Path

from failure_doctor.auto_collect import collect_project, detect_frameworks


class AutoCollectorPresetTests(unittest.TestCase):
    def test_auto_detects_common_frameworks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "playwright.config.ts").write_text("export default {}", encoding="utf-8")
            (root / "scrapy.cfg").write_text("[settings]\n", encoding="utf-8")
            (root / "package.json").write_text('{"devDependencies":{"puppeteer":"latest","cypress":"latest"}}', encoding="utf-8")
            frameworks = detect_frameworks(root, "auto")
            self.assertIn("playwright", frameworks)
            self.assertIn("scrapy", frameworks)
            self.assertIn("node_browser", frameworks)

    def test_explicit_preset_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "selenium.log").write_text("NoSuchElementException\n", encoding="utf-8")
            out = Path(tmp) / "out"
            manifest = collect_project(root, out, preset="selenium")
            self.assertEqual(manifest["preset"], "selenium")
            self.assertEqual(manifest["detected_frameworks"], ["selenium"])

