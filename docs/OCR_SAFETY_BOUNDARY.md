# OCR Safety Boundary

OCR/document evidence is local-first.

Forbidden by default:

- uploading screenshots, PDFs, or documents to any external OCR, VLM, or LLM service
- reading browser profiles, cookie stores, credential stores, SSH keys, `.env`, or broad user folders
- marking raw OCR output as safe to share before safety evaluation
- including raw sensitive OCR text in AI handoff

Allowed:

- local/mock OCR evidence extraction
- importing user-provided OCR JSON
- comparing OCR with DOM, offline VLM responses, schema, or data-quality checks
- generating redacted OCR summaries for AI handoff

OCR results are evidence, not ground truth.
