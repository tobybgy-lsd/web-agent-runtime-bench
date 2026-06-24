# Anti-Leakage Design

## Phase 5.1 Guard Rules

- Agent NEVER sees: hidden_oracle, expected_answer, db_answer, ground_truth, pass_status
- Agent NEVER accesses: /api/check-answer/, /admin/, database
- Agent input: only visible_config, api_responses, compact_text_for_model
- Oracle guard: scans all agent_input, attempts, results for leakage

## Phase 5.2 Safety

- All JS bundles are synthetic (not copied from real websites)
- All API verification is local mock (x-demo-signature, WARBDemoV1)
- No external network requests
- No real platform credentials or signatures
- No Cookie/Authorization headers
- No real website URLs in demo code

## Public Showcase

This showcase directory contains:
- Synthetic demo code only
- Sample reports with no raw data dumps
- No challenge answers or expected_answer values
- No database credentials
- No API keys

The original LearnSpider challenge pool answer data is NOT included in this showcase.
