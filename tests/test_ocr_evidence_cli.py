from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase


def write_case(root: Path, *, text: str = "Save draft") -> Path:
    inp = root / "input"
    inp.mkdir(parents=True)
    (inp / "mock_ocr_result.json").write_text(
        json.dumps(
            {
                "text_blocks": [{"text": text, "bbox": [1, 2, 30, 20], "confidence": 0.96}],
                "tables": [],
                "forms": [],
                "confidence_summary": {"overall": 0.96, "text": 0.96, "table": 0.0, "form": 0.0},
            }
        ),
        encoding="utf-8",
    )
    return inp


class OcrEvidenceCliTests(TestCase):
    def test_ocr_evidence_help_works(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "ocr-evidence", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("extract", result.stdout)

    def test_mock_ocr_extract_writes_standard_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = write_case(root)
            out = root / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "ocr-evidence",
                    "extract",
                    "--input",
                    str(inp),
                    "--out",
                    str(out),
                    "--provider",
                    "mock_ocr",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            evidence = json.loads((out / "ocr_evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["provider"], "mock_ocr")
            self.assertFalse(evidence["safety"]["cloud_upload_used"])
            self.assertEqual(evidence["text_blocks"][0]["text"], "Save draft")
            self.assertTrue((out / "document_structure.json").exists())
            self.assertTrue((out / "ocr_data_quality_report.json").exists())

    def test_compare_and_compare_vlm_work_offline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = write_case(root, text="Publish")
            out = root / "ocr"
            subprocess.run(
                [sys.executable, "-m", "failure_doctor", "ocr-evidence", "extract", "--input", str(inp), "--out", str(out)],
                check=True,
            )
            dom = root / "dom_snapshot.html"
            dom.write_text("<button>Save</button>", encoding="utf-8")
            cmp_dir = root / "cmp"
            subprocess.run(
                [sys.executable, "-m", "failure_doctor", "ocr-evidence", "compare", "--ocr", str(out), "--dom", str(dom), "--out", str(cmp_dir)],
                check=True,
            )
            dom_report = json.loads((cmp_dir / "ocr_dom_consistency_report.json").read_text(encoding="utf-8"))
            self.assertEqual(dom_report["findings"][0]["type"], "ocr_dom_text_conflict")
            vlm = root / "vlm_responses.jsonl"
            vlm.write_text(json.dumps({"selected_action": "Click Save"}) + "\n", encoding="utf-8")
            vlm_dir = root / "vlm_cmp"
            subprocess.run(
                [sys.executable, "-m", "failure_doctor", "ocr-evidence", "compare-vlm", "--ocr", str(out), "--vlm", str(vlm), "--out", str(vlm_dir)],
                check=True,
            )
            vlm_report = json.loads((vlm_dir / "ocr_vlm_consistency_report.json").read_text(encoding="utf-8"))
            self.assertEqual(vlm_report["findings"][0]["type"], "ocr_vlm_semantic_conflict")

