from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from failure_doctor.console.readers import read_console_report


class ConsoleReportReaderTests(unittest.TestCase):
    def test_console_report_reader_handles_missing_sections(self) -> None:
        with TemporaryDirectory() as tmp:
            report = Path(tmp) / "report"
            report.mkdir()
            (report / "diagnosis.json").write_text(
                json.dumps(
                    {
                        "user_facing_category": "缃戠粶/浠ｇ悊闂",
                        "technical_category": "network_transport",
                        "subtype": "tls_alpn_fingerprint_mismatch",
                        "confidence": 0.82,
                        "next_action": "Collect local TLS evidence.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            payload = read_console_report(report)

            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["summary"]["subtype"], "tls_alpn_fingerprint_mismatch")
            self.assertTrue(payload["sections"]["diagnosis"]["available"])
            self.assertFalse(payload["sections"]["evidence"]["available"])
            self.assertFalse(payload["sections"]["ai_handoff"]["available"])

    def test_console_report_reader_redacts_sensitive_values(self) -> None:
        with TemporaryDirectory() as tmp:
            report = Path(tmp) / "report"
            report.mkdir()
            (report / "diagnosis.json").write_text(
                '{"raw_error": "Authorization: Bearer sk-secret-token password=abc123"}',
                encoding="utf-8",
            )

            payload = read_console_report(report)
            rendered = json.dumps(payload, ensure_ascii=False)

            self.assertNotIn("sk-secret-token", rendered)
            self.assertNotIn("password=abc123", rendered)
            self.assertIn("[REDACTED]", rendered)


if __name__ == "__main__":
    unittest.main()

