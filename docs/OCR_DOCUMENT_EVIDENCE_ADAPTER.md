# OCR & Document Evidence Adapter

Agent Failure Doctor v3.5 treats OCR and document structure as local evidence for automation failure diagnosis.

Use it for screenshots, PDFs, forms, tables, reports, RPA exports, ecommerce SKU tables, ERP exports, and document-heavy automation failures.

```powershell
failure-doctor ocr-evidence extract --input .\screenshot.png --out .\ocr_report --provider mock_ocr
failure-doctor ocr-evidence compare --ocr .\ocr_report --dom .\dom_snapshot.html --out .\ocr_compare
failure-doctor ocr-evidence compare-vlm --ocr .\ocr_report --vlm .\vlm_responses.jsonl --out .\ocr_vlm_compare
```

OCR evidence is not ground truth. It is compared with DOM, VLM responses, exported schemas, data-quality checks, and local safety reports.

Default behavior is local-only. No screenshot, PDF, or document upload happens by default.
