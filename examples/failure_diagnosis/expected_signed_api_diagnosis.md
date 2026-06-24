# Expected Diagnosis: Signed API Failure (Negative Not Rejected)

**Failure Type**: negative_case_not_rejected
**Confidence**: high
**Status**: needs_fix

## Summary

The trace shows that a tampered payload was accepted when it should have been rejected. The run summary confirms: negative_rejected=5 but negative_cases=6. This indicates a "fake pass" risk — the verification system is not catching tampered inputs.

## Expected Output

- `diagnosis.json`: status=needs_fix, failure_type=negative_case_not_rejected, confidence=high
- `diagnosis.md`: report explaining the fake pass risk
- `codex_repair_prompt.md`: prompt directing the agent to strengthen verification logic

## Fix

Ensure that tampered payloads change the signature preimage enough to fail verification. Require both positive and negative test cases.
