# 2-Minute Demo Video Script

This is the 2-minute demo for the v3.2.1 distribution phase.

Goal: show Agent Failure Doctor as a local diagnosis backend for a failed
automation run, then hand the result to an AI coding assistant.

## Setup

Use a local fixture or any sanitized failed project folder. A safe default is:

```powershell
examples\failed_runs\proxy_network_error
```

No real platform, credential, account, or private browser profile is needed.

## Timeline

### 0:00-0:15 - Problem

Show a failed automation folder with an `error.log` and explain:

> The script failed, but the user only knows that the automation did not work.

### 0:15-0:35 - Run one command

```powershell
failure-doctor collect --project .\examples\failed_runs\proxy_network_error `
  --preset auto `
  --out .\demo_report `
  --auto-diagnose `
  --auto-handoff `
  --auto-sanitize
```

Say:

> The collector stays local, reads only the selected folder, diagnoses the
> evidence, creates a fix plan, and prepares an AI handoff pack.

### 0:35-0:55 - Open the human report

Open:

```text
demo_report\report\diagnosis.md
demo_report\report\evidence.json
demo_report\fix_plan\fix_plan.md
```

Show:

- category
- evidence
- missing evidence
- next action
- repair order

### 0:55-1:20 - Show AI handoff

Open:

```text
demo_report\ai_handoff\
```

Point to:

- Codex / Claude / Cursor instructions
- allowed commands
- forbidden actions
- safety boundary

Say:

> This is the difference between a raw error log and a repair task pack.

### 1:20-1:45 - Verify after repair

Show the verification command:

```powershell
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification
```

Open the verification report and explain that `failure-doctor verify` checks
whether the original failure was resolved, unchanged, or changed into a new
failure.

### 1:45-2:00 - Ask for real cases

End with:

> If you have a sanitized failed Playwright, Selenium, Scrapy, RPA, or AI agent
> run, open an External Failure Case issue. The goal is not stars; the goal is
> real failure samples.

## Recording Checklist

- Keep terminal font large.
- Do not show private paths, tokens, cookies, browser profiles, or customer data.
- Show `diagnosis.md`, `fix_plan.md`, and the `ai_handoff` folder.
- Do not claim CAPTCHA bypass, bot evasion, credential extraction, or
  unauthorized collection.
