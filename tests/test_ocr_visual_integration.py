from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase


class OcrVisualIntegrationTests(TestCase):
    def test_visual_diagnose_accepts_ocr_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = root / "case"
            case.mkdir()
            (case / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            (case / "dom_snapshot.html").write_text("<button>Save</button>", encoding="utf-8")
            (case / "mock_ocr_result.json").write_text(
                json.dumps({"text_blocks": [{"text": "Publish", "confidence": 0.91}]}),
                encoding="utf-8",
            )
            out = root / "out"
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "visual-diagnose", str(case), "--ocr-provider", "mock_ocr", "--out", str(out)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads((out / "visual_diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["ocr_evidence"]["provider"], "mock_ocr")
