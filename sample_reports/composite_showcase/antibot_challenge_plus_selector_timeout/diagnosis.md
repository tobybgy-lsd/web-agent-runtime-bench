# antibot_challenge_plus_selector_timeout

## Primary Failure
- `anti_bot_risk` / `captcha_or_challenge_page`

## Secondary Failures
- `selector_drift` / `timeout_waiting_for_selector`

## Blocking Failure
- access-control boundary blocks downstream page selectors

## Repair Order
- Confirm authorization and use an official API, authorized export, manual review, or stop automation if access is unclear.
- Only after the compliant path is confirmed, re-run selectors.
