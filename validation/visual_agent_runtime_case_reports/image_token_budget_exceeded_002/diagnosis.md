# Visual Runtime Diagnosis

Conclusion: `visual_runtime_safety_blocked` at confidence `0.98`.

## Evidence

- sensitive screenshot, OCR, or VLM-response evidence requires sanitization

## Safe Next Action

Stop sharing this artifact until sensitive visual evidence is redacted or removed.

## Suggested Fix Plan

- Re-run with the same offline artifact capture settings.
- Check screenshot freshness, viewport/DPR metadata, and action-coordinate mapping before changing app code.
- If evidence is insufficient, request a fuller local visual-run pack and manual review.

## Verification

Capture a new local visual-run artifact and compare profile, grounding, coordinate, and stale-observation reports.
