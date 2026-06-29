# P98 Controlled Maturity Scorecard

本评分不计算生态成熟度。
生态成熟度包括 stars、external PR、external issue、PyPI 下载量、第三方集成采用、真实用户长期反馈。本轮不评价。

本轮只评价可控成熟度：项目自己可以通过代码、验证资产、文档、安全边界和 CI 稳定性持续改进的部分。

## P98 Pillars

1. Playwright Trace Doctor P98
2. Cross-Framework Adapter P98
3. Training Challenge Sedimentation P98
4. Composite + Counterfactual Diagnosis P98
5. AI Handoff + Patch Proposal P98
6. Batch / Fleet Diagnosis P98
7. Sanitization + Shareable Pack P98
8. Safety Boundary P98
9. Release / Docs / Dashboard P98

## Global Gate

P98 pass requires:

- all required validation files exist
- all required validation runners exist
- all runners pass
- forbidden_output_count = 0 in every track
- severe_misclassification <= allowed threshold in every track
- no real-platform access in tests/examples
- no private solution leakage
- no secrets
- unit tests pass
- smoke test pass
- safety scan pass
- CI green
- dashboard shows actual numbers, not target-only metrics
- no track hidden because its result is lower

## Non-Goals

- No CAPTCHA bypass.
- No bot evasion.
- No fingerprint spoofing.
- No dynamic signature cracking.
- No real-platform access or production crawling in tests/examples.
- No private solution leakage from training challenges or authorized labs.

