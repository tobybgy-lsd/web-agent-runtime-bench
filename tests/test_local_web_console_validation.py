from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


class LocalWebConsoleValidationTests(unittest.TestCase):
    def test_local_web_console_validation_runner_passes(self) -> None:
        subprocess.run(
            [sys.executable, "tools/validation/run_local_web_console_validation.py"],
            check=True,
        )
        payload = json.loads(Path("validation/local_web_console_validation.json").read_text())

        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 80)
        self.assertTrue(payload["binds_to_127_0_0_1_by_default"])
        self.assertTrue(payload["rejects_0_0_0_0_without_allow_lan"])
        self.assertEqual(payload["external_request_count"], 0)
        self.assertEqual(payload["cdn_reference_count"], 0)


if __name__ == "__main__":
    unittest.main()

