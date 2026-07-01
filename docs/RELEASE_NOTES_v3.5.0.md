# Agent Failure Doctor v3.5.0 - OCR & Document Evidence Adapter Pack

## What changed

v3.5.0 adds a local-first OCR/document evidence adapter so screenshots, PDFs, forms, tables, reports, invoices, RPA exports, ecommerce SKU tables, and ERP exports can become structured diagnosis evidence.

## New CLI

```powershell
failure-doctor ocr-evidence extract --input .\screenshot.png --out .\ocr_report --provider mock_ocr
failure-doctor ocr-evidence compare --ocr .\ocr_report --dom .\dom_snapshot.html --out .\ocr_compare
failure-doctor ocr-evidence compare-vlm --ocr .\ocr_report --vlm .\vlm_responses.jsonl --out .\ocr_vlm_compare
failure-doctor ocr-evidence validate --input .\ocr_report --out .\ocr_validation
```

## Provider Policy

- Default provider is `mock_ocr`.
- PaddleOCR and PaddleOCR-VL are optional local providers.
- Baidu cloud OCR/doc parsing providers are disabled by default.
- Cloud OCR requires explicit `--allow-cloud-ocr` and safety evaluation.
- Sensitive documents are blocked or require sanitization.

## OCR-DOM Consistency

Compares visible OCR text, form labels, and table evidence with DOM snapshots.

## OCR-VLM Consistency

Compares OCR evidence with existing offline `vlm_responses.jsonl`. It does not call an external VLM.

## OCR Data-Quality Integration

OCR table and form evidence feeds schema, table, required-field, type, and duplicate-row checks.

## Safety Boundary

OCR evidence is not ground truth. It is supporting evidence. No screenshot, PDF, or document upload happens by default.

Safety:

- Cloud OCR is disabled by default.
- External OCR calls are not made during validation.
- Sensitive document evidence is blocked or routed to sanitization.
- Forbidden output count is 0 in the v3.5 validation gate.

## Validation Metrics

- OCR/document evidence cases: 148
- External OCR calls: 0
- Document uploads: 0
- Sensitive data blocking: 100%
- P98 OCR pillar: pass

## Install

```powershell
python -m pip install agent-failure-doctor==3.5.0
failure-doctor ocr-evidence --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

Optional extras:

```powershell
python -m pip install "agent-failure-doctor[ocr]"
python -m pip install "agent-failure-doctor[paddleocr]"
python -m pip install "agent-failure-doctor[baidu-ocr]"
```

## Reproduce

```powershell
python -m tools.validation.run_ocr_document_evidence_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

## Known limits

- OCR evidence is supporting evidence, not ground truth.
- PaddleOCR and PaddleOCR-VL are optional local providers.
- Baidu OCR providers are policy-gated and disabled by default.
- This release does not upload screenshots, PDFs, or documents by default.
