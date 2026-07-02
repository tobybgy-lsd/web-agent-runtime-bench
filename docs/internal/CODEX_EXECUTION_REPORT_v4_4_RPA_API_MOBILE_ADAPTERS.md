# Codex Execution Report: v4.4 RPA, API, and Mobile Adapter Pack

## Scope

Added public-safe adapter entry points for desktop RPA, API automation, and mobile automation failure evidence. These adapters normalize logs and metadata into a shared failure pack shape and produce safe diagnostic categories without publishing private solver logic or bypass recipes.

## Public Capabilities

- `failure-doctor adapter rpa normalize|diagnose`
- `failure-doctor adapter api normalize|diagnose`
- `failure-doctor adapter mobile normalize|diagnose`
- `failure-doctor collect --adapter rpa-uipath-mock|api-postman-newman|mobile-appium-mock`

## Safety Boundary

Adapters describe evidence and compliant next actions only. They do not output CAPTCHA bypass, bot evasion, credential extraction, protected-signature cracking, or real-platform scraping instructions.

## Verification

Use:

```powershell
python -m unittest tests.test_v44_adapters -b
python -m tools.validation.run_desktop_rpa_adapter_validation
python -m tools.validation.run_api_automation_adapter_validation
python -m tools.validation.run_mobile_automation_adapter_validation
```
