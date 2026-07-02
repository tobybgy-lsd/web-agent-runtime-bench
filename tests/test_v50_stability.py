from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import main
from failure_doctor.stability.core import STABLE_COMMAND_GROUPS, STABLE_SCHEMAS


class StabilityCliTests(unittest.TestCase):
    def test_stable_contracts_include_new_command_groups(self) -> None:
        self.assertIn("adapter", STABLE_COMMAND_GROUPS)
        self.assertIn("deploy", STABLE_COMMAND_GROUPS)
        self.assertIn("stability", STABLE_COMMAND_GROUPS)
        self.assertIn("plugin_manifest", STABLE_SCHEMAS)

    def test_stability_cli_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "api"
            schema = root / "schema"
            abi = root / "abi"
            self.assertEqual(main(["stability", "check-api", "--out", str(api)]), 0)
            self.assertEqual(main(["stability", "check-schema", "--out", str(schema)]), 0)
            self.assertEqual(main(["stability", "check-plugin-abi", "--out", str(abi)]), 0)
            payload = json.loads((api / "api_contract_report.json").read_text(encoding="utf-8"))
            self.assertTrue(payload["stable_cli_contract_pass"])


if __name__ == "__main__":
    unittest.main()

