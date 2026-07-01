# Pure Visual Agent Runtime Evaluation

`failure-doctor visual-runtime` diagnoses offline screenshot-driven agent runs
without requiring DOM evidence.

```powershell
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor visual-runtime profile --input .\visual_run --out .\visual_profile
failure-doctor visual-runtime compare --baseline .\run_a --candidate .\run_b --out .\compare_report
```

The runtime profile tracks screenshot capture and transport cost, image-token
estimates, VLM observation metadata, action grounding, click-coordinate drift,
DPR and viewport mismatch, stale observations, OCR semantic mismatch, visual
context loss, and optional DOM conflict.

Default behavior is offline and local:

- no external VLM call
- no screenshot upload
- no real platform session
- no browser profile access
- no behavioral mimicry or protected challenge automation guidance

When evidence is insufficient, the tool asks for a fuller local visual-run pack
instead of guessing.
