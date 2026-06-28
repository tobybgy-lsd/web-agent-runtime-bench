# Anti-Bot Risk Boundary

Agent Failure Doctor identifies likely anti-bot or access-control risk, but does not provide bypass instructions.

## Failure Layer

`failure_layer: anti_bot_risk`

## Subtypes

- `rate_limited`
- `captcha_or_challenge_page`
- `fingerprint_risk`
- `dynamic_signature_required`
- `ip_reputation_block`
- `behavioral_risk`
- `auth_or_permission_block`

## Allowed Output

- identify likely risk or access-control evidence
- explain why the failure is not a normal selector, storage, or proxy bug
- recommend confirming authorization
- recommend official APIs, authorized export, manual review, or contacting the platform owner
- recommend reducing request volume where appropriate
- recommend stopping the run when authorization or platform terms are unclear

## Forbidden Output

- challenge defeat instructions
- access-control defeat instructions
- fingerprint manipulation instructions
- private request validation reverse engineering
- ban avoidance workflows
- account rotation workflows
- network rotation workflows
- automated challenge solving
- unauthorized collection guidance

## Safety Rule

When evidence is thin, downgrade to `insufficient_evidence`. When evidence indicates a challenge or access-control layer, route to compliant next actions only.
