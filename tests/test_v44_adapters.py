from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import main


class AdapterCliTests(unittest.TestCase):
    def test_rpa_adapter_diagnoses_control_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "rpa.log"
            inp.write_text("RPA control not found after selector changed", encoding="utf-8")
            out = root / "out"
            self.assertEqual(main(["adapter", "rpa", "diagnose", "--input", str(inp), "--out", str(out)]), 0)
            payload = json.loads((out / "adapter_diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["failure_type"], "desktop_rpa_automation")
            self.assertEqual(payload["subtype"], "rpa_selector_drift")
            self.assertEqual(payload["forbidden_output_count"], 0)

    def test_api_adapter_keeps_rate_limit_guidance_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "newman.json"
            inp.write_text('{"status":429,"error":"rate limited"}', encoding="utf-8")
            out = root / "out"
            self.assertEqual(main(["adapter", "api", "diagnose", "--input", str(inp), "--out", str(out)]), 0)
            payload = json.loads((out / "adapter_diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["subtype"], "api_rate_limited")
            actions = "\n".join(payload["safe_next_action"]).lower()
            self.assertIn("official api", actions)
            self.assertNotIn("proxy pool", actions)

    def test_mobile_adapter_and_collect_shortcut_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "appium.log"
            inp.write_text("mobile context mismatch and density issue", encoding="utf-8")
            out = root / "collect"
            self.assertEqual(
                main(["collect", "--adapter", "mobile-appium-mock", "--input", str(inp), "--out", str(out)]),
                0,
            )
            payload = json.loads((out / "adapter_normalized.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["adapter_kind"], "mobile")
            self.assertTrue(payload["local_only"])


if __name__ == "__main__":
    unittest.main()
