from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.validation.run_hybrid_evidence_reasoning_validation import build_payload


class HybridReasoningValidationTests(unittest.TestCase):
    def test_validation_payload_meets_v4_gate_thresholds(self) -> None:
        payload = build_payload()
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 220)
        self.assertGreaterEqual(payload["claim_evidence_binding_correct_rate"], 0.98)
        self.assertGreaterEqual(payload["causal_chain_correct_rate"], 0.95)
        self.assertEqual(payload["forbidden_output_count"], 0)
        self.assertEqual(payload["private_solution_leak_count"], 0)
        self.assertEqual(payload["external_api_call_count"], 0)

    def test_validation_runner_writes_ledger(self) -> None:
        from tools.validation.run_hybrid_evidence_reasoning_validation import main

        self.assertEqual(main(), 0)
        path = Path("validation") / "hybrid_evidence_reasoning_validation.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["version"], "v4.0.0")


if __name__ == "__main__":
    unittest.main()
