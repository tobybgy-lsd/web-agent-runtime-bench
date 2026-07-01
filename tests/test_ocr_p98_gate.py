from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


class OcrP98GateTests(TestCase):
    def test_p98_gate_contains_ocr_pillar(self) -> None:
        subprocess.run([sys.executable, "-m", "tools.validation.run_ocr_document_evidence_validation"], check=True)
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_p98_master_gate"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(Path("validation/p98_master_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["pillars"]["ocr_document_evidence_adapter"]["status"], "pass")
