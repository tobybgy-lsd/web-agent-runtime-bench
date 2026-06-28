# Regression Snapshot: Chromium sandbox 权限问题

## Expected Behavior

- Scenario: Chromium sandbox 权限问题
- Expected technical category: $tech
- If logs are weak, downgrade to insufficient_evidence instead of hard guessing.

## Misclassification Guard

This snapshot exists to prevent v0.5 hardening from confusing Chromium sandbox 权限问题 with unrelated selector or business-logic failures.

## Required Next Action

Generate a bounded Codex fix prompt, preserve local-first evidence, and do not add CAPTCHA bypass, bot evasion, credentials, cookies, tokens, or platform scraping behavior.
