# Visual Runtime Diagnosis

Conclusion: `pure_visual_insufficient_evidence` at confidence `0.45`.

## Evidence

- pure visual run lacks click, OCR, or VLM-response evidence

## Safe Next Action

Manual review required: add OCR, click metadata, viewport/DPR, or adjacent frames before classifying the run.

## Suggested Fix Plan

- Re-run with the same offline artifact capture settings.
- Check screenshot freshness, viewport/DPR metadata, and action-coordinate mapping before changing app code.
- If evidence is insufficient, request a fuller local visual-run pack and manual review.

## Verification

Capture a new local visual-run artifact and compare profile, grounding, coordinate, and stale-observation reports.
