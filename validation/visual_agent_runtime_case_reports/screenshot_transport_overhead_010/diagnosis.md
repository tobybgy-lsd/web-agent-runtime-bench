# Visual Runtime Diagnosis

Conclusion: `screenshot_transport_overhead` at confidence `0.84`.

## Evidence

- screenshot payload size or transfer cost is high

## Safe Next Action

Inspect the offline visual timeline and repair the capture/grounding/coordinate pipeline with local evidence only.

## Suggested Fix Plan

- Re-run with the same offline artifact capture settings.
- Check screenshot freshness, viewport/DPR metadata, and action-coordinate mapping before changing app code.
- If evidence is insufficient, request a fuller local visual-run pack and manual review.

## Verification

Capture a new local visual-run artifact and compare profile, grounding, coordinate, and stale-observation reports.
