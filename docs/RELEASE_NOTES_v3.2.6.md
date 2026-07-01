# Agent Failure Doctor v3.2.6 - JavaScript Integrity Evidence Patch

v3.2.6 is a patch release for the v3.2 Auto Collector line. It adds
public-safe diagnosis for user-supplied JavaScript/request-integrity evidence
while preserving the project boundary: local-first diagnosis only, no default
active probes, no signature reconstruction, and no bypass guidance.

## What changed

- Added `js_integrity_report.json` as a recognized offline evidence input.
- Added public-safe anti-bot risk subtypes:
  - `obfuscated_js_integrity_required`
  - `js_ast_obfuscation_detected`
  - `rotated_string_array_detected`
  - `client_generated_token_missing`
  - `request_integrity_algorithm_changed`
- Added `docs/JS_INTEGRITY_BOUNDARY.md` to document what may be published and
  what must remain local/private.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.2.6
failure-doctor --help
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

PyPI: <https://pypi.org/project/agent-failure-doctor/>

For local development from source:

```powershell
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
python -m tools.validation.run_p98_master_gate
```

## Safety

This release keeps JavaScript integrity signals as evidence-only diagnostics.
It does not ship AST recovery recipes, signature formulas, private constants,
token reconstruction, challenge flags, CAPTCHA bypass, anti-bot evasion,
fingerprint spoofing, or default active probes.

Expected safety result:

```text
forbidden outputs: 0
private solution leaks: 0
real platform access: 0
```

## Known limits

- `js_integrity_report.json` is a user-supplied summary. Agent Failure Doctor
  does not verify how it was collected.
- These subtypes identify risk boundaries and evidence needs; they do not
  generate operational deobfuscation or bypass steps.
- If evidence is weak or authorization is unclear, the safe next action is to
  stop automation or use an official, authorized path.
