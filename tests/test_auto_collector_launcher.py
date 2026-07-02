import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutoCollectorLauncherTests(unittest.TestCase):
    def test_windows_launchers_exist_and_are_portable(self):
        bat = ROOT / "scripts" / "windows" / "Start-FailureDoctor-Diagnosis.bat"
        ps1 = ROOT / "scripts" / "windows" / "Start-FailureDoctor-Diagnosis.ps1"
        self.assertTrue(bat.exists())
        self.assertTrue(ps1.exists())
        text = bat.read_text(encoding="utf-8") + ps1.read_text(encoding="utf-8")
        self.assertIn("failure-doctor collect", text)
        self.assertIn("--auto-diagnose", text)
        self.assertNotIn("D:\\", text)
        self.assertNotIn("Administrator", text)


