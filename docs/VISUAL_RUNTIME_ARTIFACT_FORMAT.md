# Visual Runtime Artifact Format

Expected layout:

```text
visual_run/
  run_manifest.json
  screenshots_manifest.json
  frames/step_001.png
  observations.jsonl
  actions.jsonl
  coordinate_clicks.jsonl
  viewport.jsonl
  dpr.jsonl
  ocr_excerpt.jsonl
  vlm_responses.jsonl
  dom_snapshots/step_001.html
  expected_outcome.json
```

`run_manifest.json` must declare:

```json
{
  "schema_version": "visual_run/v1",
  "run_id": "example",
  "source": "generic_screenshot_agent",
  "mode": "pure_visual",
  "local_only": true,
  "no_external_upload": true,
  "no_real_platform_access": true,
  "created_at": "2026-07-01T00:00:00+00:00"
}
```

DOM is optional. Use `--no-dom` for pure visual analysis and `--dom-optional`
when DOM snapshots may or may not exist.
