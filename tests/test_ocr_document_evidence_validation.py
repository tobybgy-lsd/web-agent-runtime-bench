from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


class OcrDocumentEvidenceValidationTests(TestCase):
    def test_validation_runner_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_ocr_document_evidence_validation"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(Path("validation/ocr_document_evidence_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 130)
        self.assertEqual(payload["external_ocr_call_count"], 0)

