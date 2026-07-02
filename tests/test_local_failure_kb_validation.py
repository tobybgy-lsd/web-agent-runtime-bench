from __future__ import annotations

import unittest

from tools.validation.run_local_failure_kb_validation import main


class LocalFailureKbValidationRunnerTests(unittest.TestCase):
    def test_validation_runner_passes_thresholds(self) -> None:
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()

