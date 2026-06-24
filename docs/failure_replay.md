# Failure Replay & Capability Dashboard

## Trace → Replay Pipeline

The runtime benchmark produces structured traces that feed into failure replay and capability dashboards:

```
variant_trace.jsonl → failure_replay.md + capability_dashboard.md
```

## Trace Format (JSONL)

Each line records one variant run:

```json
{
  "variant_name": "missing_navigator",
  "bundle": "bundle_navigator_required.js",
  "expected_error": "missing_navigator",
  "actual_error": "missing_navigator",
  "status": "CLASSIFIED_OK",
  "rc": 1,
  "stderr_preview": "ReferenceError: navigator is not defined",
  "classifier_confidence": 0.93,
  "timestamp": "2026-06-24T12:00:00"
}
```

## Failure Replay Index

The `failure_replay.md` output groups failures by:

1. **Error type**: missing_window / missing_document / missing_navigator / missing_event_target / missing_local_storage
2. **Root cause**: Which global API was absent
3. **Repair action**: Which shim module to load
4. **Repair outcome**: Whether the same bundle succeeds after shim repair

### Repair Flow

```
1. Run bundle without shim → ReferenceError
2. Classifier identifies error_type
3. Load synthetic_browser_shim.js before bundle
4. Re-run → success
5. Call __warb_demo_sign() → verified by mock API
```

## Capability Dashboard

The dashboard tracks:

| Metric | Description |
|--------|-------------|
| Failure cases | Number of runtime contract violations |
| Classified failures | Failures correctly identified by classifier |
| Unknown errors | Failures classifier could not label |
| Success cases | Full shim runs that passed |
| Mock API accepted | Signature verification passed |

### A2 Dashboard Sample

| Metric | Count |
|--------|------:|
| failure_cases | 5 |
| classified_failures | 5 |
| unknown_errors | 0 |
| success_cases | 5 |
| full_shim_success_count | 5 |
| mock_api_accepted_count | 5 |
| external_network | 0 |
| overall_status | PASS |
