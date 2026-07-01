# OCR Visual Runtime Integration

`visual-diagnose` and `visual-runtime diagnose` can include OCR evidence:

```powershell
failure-doctor visual-diagnose .\case --ocr-provider mock_ocr --out .\visual_report
failure-doctor visual-runtime diagnose --input .\visual_run --ocr-provider mock_ocr --out .\visual_runtime_report
```

This adds local OCR evidence summaries and OCR runtime metrics:

- `ocr_step_confidence`
- `ocr_target_persistence`
- `ocr_text_drift`
- `ocr_vlm_conflict_rate`
- `ocr_compression_loss_score`

No external OCR or VLM call is made by these integrations.
