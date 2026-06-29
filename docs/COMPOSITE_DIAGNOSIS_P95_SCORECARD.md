# Composite Diagnosis P95 Scorecard

P95 is not a blended average. P95 requires each core capability and each failure
family to pass at or above 95 percent.

## Metrics

- primary_failure_correct
- secondary_failure_detected
- blocking_failure_correct
- downstream_failure_correct
- competing_hypothesis_preserved
- repair_order_correct
- evidence_graph_valid
- confidence_calibrated
- partial_resolution_status_correct
- changed_failure_status_correct
- overconfident_wrong
- forbidden_output

## Global Gate

Pass if:

- total_cases >= 120
- primary_failure_correct >= 114/120
- secondary_failure_detected >= 114/120
- blocking_failure_correct >= 114/120
- downstream_failure_correct >= 114/120
- repair_order_correct >= 114/120
- evidence_graph_valid >= 114/120
- verification_status_correct >= 57/60
- overconfident_wrong <= 2
- severe_misclassification <= 3
- forbidden_output = 0

## Per-Family Gate

Each family must pass:

- cases_per_family >= 20
- primary_failure_correct >= 19/20
- blocking_failure_correct >= 19/20
- repair_order_correct >= 19/20
- forbidden_output = 0

Families:

1. auth_selector_composites
2. route_har_network_composites
3. antibot_downstream_composites
4. network_environment_navigation_composites
5. dom_frame_shadow_selector_composites
6. website_change_business_logic_composites

If any family fails, the overall P95 gate fails.

## Safety Boundary

Composite diagnosis is local-first and deterministic. It does not provide
CAPTCHA bypass, bot evasion, fingerprint spoofing, dynamic signature cracking,
IP pools, account pools, ban evasion, or unauthorized scraping guidance.
