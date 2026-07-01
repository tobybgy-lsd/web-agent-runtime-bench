# Visual Agent Runtime Observability

Agent Failure Doctor v3.4 adds offline observability for screenshot-driven AI
browser agents, RPA flows, and Computer Use style runs.

The goal is to explain why an agent saw a page, chose an action, clicked a
coordinate, and then failed.

It analyzes:

- screenshot capture and image payload cost
- local VLM observation metadata or deterministic mock responses
- action grounding confidence
- coordinate clicks and target bounding boxes
- DPR and viewport scroll drift
- stale screenshots and delayed actions
- OCR text mismatch
- optional DOM versus visual conflict

It does not call external VLMs by default, upload screenshots, access real
platforms, or provide access-control defeat guidance.

## Commands

```powershell
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor visual-runtime profile --input .\visual_run --out .\visual_profile
failure-doctor visual-runtime compare --baseline .\run_a --candidate .\run_b --out .\compare_report
failure-doctor visual-runtime adapt --source generic --input .\artifact_dir --out .\visual_run
failure-doctor visual-runtime validate --input .\visual_run --out .\validation_report
```

## Evidence Boundary

The visual runtime pack is evidence-only. It can say that coordinate drift,
viewport mismatch, stale observation, or visual grounding failed. It should not
generate anti-detection behavior, protected-site challenge automation, or
instructions to imitate a person.
