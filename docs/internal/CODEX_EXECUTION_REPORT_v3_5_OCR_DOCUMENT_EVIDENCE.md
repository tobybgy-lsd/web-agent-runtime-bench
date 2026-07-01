# Codex Execution Report: v3.5 OCR Document Evidence

## Goal

Add local-first OCR and document evidence as a first-class failure diagnosis source.

## Starting Version

v3.4.0 Visual Agent Runtime Observability.

## New CLI

`failure-doctor ocr-evidence extract|compare|compare-vlm|validate`.

## Providers

`mock_ocr`, `paddleocr_local`, `paddleocr_vl_local`, `baidu_cloud_ocr`, `baidu_cloud_doc_parser`, and `external_json_import`.

## Provider Safety Strategy

Mock/local/imported providers are local-only. Cloud providers are blocked by default and require explicit authorization. Sensitive OCR input blocks cloud execution.

## Evidence Schema

Added OCR evidence, OCR block, document structure, table structure, form structure, DOM consistency, VLM consistency, data quality, provider config, and validation result schemas.

## Consistency and Quality

OCR-DOM, OCR-VLM, and OCR data-quality reports are generated locally.

## Visual Integration

`visual-diagnose` and `visual-runtime diagnose` accept `--ocr-provider mock_ocr`.

## Agent Bootstrap

Agent bootstrap now writes `ocr_evidence_workflow.md` for supported agent frontends.

## Validation

The validation runner generates 148 local-only mock OCR/document cases. It records zero external OCR calls and zero document uploads.

## Remaining Limits

PaddleOCR and Baidu providers are policy stubs unless the user explicitly configures optional dependencies or credentials. The public package does not implement cloud upload by default.
