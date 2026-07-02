# Console Report Viewer

The console report reader accepts directories produced by the existing CLI
lifecycle:

- `diagnosis.json` / `diagnosis.md`
- `evidence.json`
- `repair_suggestions.md`
- `issue_draft.md`
- `codex_fix_prompt.md`
- `ai_handoff.json`
- `patch_proposal.json`
- `patch_safety_report.json`
- `visual_runtime_profile.json`
- `ocr_evidence.json`
- `regulated_eval_result.json`
- `batch_report.json`
- `full_chain_eval.json`
- `verification_report.json`
- `shareability_decision.json`
- `safety_evaluation_report.json`

If a section is missing, the console marks it unavailable. This lets a small
diagnosis-only report and a full-chain report use the same viewer.

Sensitive-looking values in report text are redacted before they are returned
through the console API.
