# Console Operations

## Common Commands

```powershell
failure-doctor console
failure-doctor console --import-report .\report --open
failure-doctor console --workspace .\.failure-doctor-console --readonly
```

## Manual Smoke Test

```powershell
failure-doctor console --host 127.0.0.1 --port 8765 --workspace .\.failure-doctor-console
```

Open:

```text
http://127.0.0.1:8765/
```

Expected:

- Dashboard loads.
- `/api/status` returns `local_only=true`.
- Static assets are served from `/static/`.
- No external network asset is required.
- POST routes reject requests without `X-Console-Token`.

## Validation

```powershell
python -m tools.validation.run_local_web_console_validation
python -m tools.validation.run_p98_master_gate
```

The v3.7 validation must report at least 80 local console cases and zero
external requests, CDN references, raw local exposure, private solution leaks,
or real-platform access.
