#!/usr/bin/env python
"""Failure Diagnosis CLI v1 — rule-based diagnosis for web agent runtime/benchmark traces.

Reads run_summary.json, trace.jsonl, and/or failure_replay.md from a synthetic
benchmark directory, identifies failure types, and generates:
  - diagnosis.json (structured)
  - diagnosis.md (human-readable)
  - codex_repair_prompt.md (actionable for coding agents)

All rules are local/synthetic. No LLM calls. No external network.

Usage:
  python tools/diagnostics/diagnose_failure.py --input-dir examples/failure_diagnosis --out-dir outputs/diagnosis_sample
  python tools/diagnostics/diagnose_failure.py --run-summary file.json --trace file.jsonl --out-dir outputs/dx
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

DIAGNOSIS_TEMPLATE = """## Diagnosis Summary

- Status: {status}
- Failure Type: {failure_type}
- Confidence: {confidence}
- Target Agent: {target_agent}
- Synthetic Only: Yes

## Evidence

{evidence_block}

## Likely Cause

{likely_cause}

## Recommended Fix

{fix_block}

## Validation Command

{validation_block}

## Safety Boundary

- This diagnosis is based on synthetic / local mock data only.
- No real platforms were accessed.
- No real signatures, no Cookie / Authorization, no external network.
"""

CODEX_PROMPT_TEMPLATE = """## Task: Repair {failure_type}

You are acting as a coding agent (Codex / WorkBuddy). A web agent runtime or benchmark trace
has been diagnosed with the following failure.

### Evidence

{evidence_block}

### Likely Cause

{likely_cause}

### Files You May Modify

Only files within the synthetic benchmark or demo directories. Do NOT modify:
- Real platform logic
- Real API endpoints
- Network request code
- Cookie / Authorization headers
- x-s / x-t / x-s-common fields

### Recommended Fix Direction

{fix_block}

### Validation After Fix

Run the following command and confirm the output shows no failure:

```
{validation_block}
```

### Output Format After Fix

Report:
- What was changed
- Which file(s) were modified
- Validation command result
- Whether the failure is resolved
- Synthetic only: YES
"""


def load_input(run_summary_path=None, trace_path=None, failure_replay_path=None, input_dir=None):
    run_summary = {}
    trace_lines = []
    if input_dir:
        rp = Path(input_dir) / "missing_runtime_run_summary.json"
        tp = Path(input_dir) / "missing_runtime_trace.jsonl"
        if rp.exists():
            run_summary_path = str(rp)
        if tp.exists():
            trace_path = str(tp)
    if run_summary_path and os.path.exists(run_summary_path):
        with open(run_summary_path, encoding="utf-8") as f:
            run_summary = json.load(f)
    if trace_path and os.path.exists(trace_path):
        with open(trace_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        trace_lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        trace_lines.append({"raw": line})
    return run_summary, trace_lines


def diagnose(run_summary, trace_lines, target_agent="codex"):
    evidence = []
    status = "unknown"
    failure_type = "unknown"
    confidence = "low"
    likely_cause = "unable to classify failure from available data"
    recommended_fix = ["inspect trace manually", "add new diagnostic pattern", "rerun smoke test"]
    validation_cmd = ["./scripts/smoke_test.ps1"]

    # Flatten all text for pattern matching
    rs_text = json.dumps(run_summary).lower()
    trace_text = "\n".join(json.dumps(t).lower() for t in trace_lines)
    combined = f"{rs_text}\n{trace_text}"

    # Rule 1: all PASS
    if (run_summary.get("overall_status") == "PASS"
            and run_summary.get("verified_cases", 0) >= 6
            and run_summary.get("negative_rejected", 0) >= 6):
        status = "pass"
        failure_type = "no_action_needed"
        confidence = "high"
        likely_cause = "benchmark passed; all positive verifications and negative rejections succeeded"
        recommended_fix = []
        validation_cmd = ["./scripts/smoke_test.ps1"]
        evidence.append("overall_status=PASS, verified_cases>=6, negative_rejected>=6")
    else:
        status = "needs_fix"

    # Rule 2: missing_window
    if "missing_window" in combined or "window is not defined" in combined:
        failure_type = "missing_window"
        confidence = "high"
        likely_cause = "JS bundle expects browser window object but current runtime lacks it"
        recommended_fix = [
            "load synthetic_browser_shim.js before the bundle",
            "rerun A0 runtime demo to verify shim repair",
            "verify classifier output shows missing_window → with_shim success",
        ]
        validation_cmd = [
            "python demo/phase5_2_runtime/run_synthetic_runtime_demo.py --out-dir sample_run/a0 --node node"
        ]
        evidence.append("found missing_window or 'window is not defined' in trace/run_summary")

    # Rule 3: missing_document
    if "missing_document" in combined or "document is not defined" in combined:
        failure_type = "missing_document"
        confidence = "high"
        likely_cause = "JS bundle expects document object but runtime provides none or partial stub"
        recommended_fix = [
            "add document stub with querySelector + createElement",
            "ensure synthetic_browser_shim.js is loaded before bundle",
        ]
        evidence.append("found missing_document or 'document is not defined' in trace")

    # Rule 4: missing_navigator
    if "missing_navigator" in combined or "navigator is not defined" in combined:
        failure_type = "missing_navigator"
        confidence = "high"
        likely_cause = "JS bundle accesses navigator.userAgent but navigator is not defined"
        recommended_fix = [
            "add navigator stub with userAgent: 'WebAgentRuntimeBench/SyntheticRuntime/1.0'",
            "ensure synthetic_browser_shim.js provides navigator",
        ]
        evidence.append("found missing_navigator or 'navigator is not defined' in trace")

    # Rule 5: missing_localStorage
    if "missing_local_storage" in combined or "localstorage is not defined" in combined:
        failure_type = "missing_local_storage"
        confidence = "high"
        likely_cause = "JS bundle accesses localStorage.getItem but localStorage is not defined"
        recommended_fix = [
            "add localStorage stub with getItem/setItem",
            "enable synthetic localStorage shim in synthetic_browser_shim.js",
        ]
        evidence.append("found missing_local_storage or 'localStorage is not defined' in trace")

    # Rule 6: missing EventTarget
    if "missing_event_target" in combined or "eventtarget is not defined" in combined:
        failure_type = "missing_event_target"
        confidence = "high"
        likely_cause = "JS bundle uses EventTarget constructor but class is not defined"
        recommended_fix = [
            "define SyntheticEventTarget class in runtime shim",
            "ensure synthetic_browser_shim.js exports EventTarget",
        ]
        evidence.append("found missing_event_target or 'EventTarget is not defined' in trace")

    # Rule 7: bundle function not registered (only if no more specific rule matched already)
    if failure_type == "unknown":
        if "sign_function_resolved" in rs_text and "false" in rs_text.split("sign_function_resolved")[1][:20] \
                or "function not registered" in combined:
            failure_type = "bundle_function_not_registered"
            confidence = "medium"
            likely_cause = "JS bundle loaded but sign function was not registered on window"
            recommended_fix = [
                "verify bundle was loaded AFTER synthetic_browser_shim.js",
                "run 'node --check' on bundle JS file to detect syntax errors",
                "check console output for ReferenceError before function registration point",
            ]
            evidence.append("sign_function_resolved=false or function not registered")

    # Rule 8: signed API verification failure
    vc = run_summary.get("verified_cases", 0)
    sc = run_summary.get("signed_cases", 0)
    if vc < sc or run_summary.get("mock_api_accepted_count", 0) < sc:
        failure_type = "signed_api_verification_failure"
        confidence = "high"
        likely_cause = f"verified_cases ({vc}) < signed_cases ({sc}); signature verification mismatched"
        recommended_fix = [
            "verify signature computation matches WARBDemoV2 on both Python and JS sides",
            "check stable_json produces identical output in both languages",
            "ensure dependency keys are aligned (e.g., 'salt_source' not 'salt')",
            "rerun A3 signed API benchmark",
        ]
        evidence.append(f"verified_cases={vc} < signed_cases={sc}")
    if "signature_mismatch" in combined or '"accepted": false' in combined:
        failure_type = "signed_api_verification_failure"
        confidence = "high"
        evidence.append("found signature_mismatch or accepted=false in trace")

    # Rule 9: negative case not rejected
    nr = run_summary.get("negative_rejected", 0)
    nc = run_summary.get("negative_cases", 0)
    if nr < nc:
        failure_type = "negative_case_not_rejected"
        confidence = "high"
        likely_cause = f"negative_rejected ({nr}) < negative_cases ({nc}); tampered payload was accepted when it should be rejected"
        recommended_fix = [
            "strengthen verification logic: tampered payload must change signature preimage",
            "ensure negative case uses different payload hash from original",
            "rerun A3 signed API benchmark",
            "require BOTH positive verification AND negative rejection for each case",
        ]
        evidence.append(f"negative_rejected={nr} < negative_cases={nc}")
    if "fake_pass" in combined or "negative accepted" in combined.lower().replace(" ", "_"):
        failure_type = "negative_case_not_rejected"
        confidence = "high"
        evidence.append("found fake_pass or negative accepted in trace")

    # Rule 10: unknown
    if failure_type == "unknown":
        status = "unknown"
        confidence = "low"
        likely_cause = "no known failure pattern matched; manual inspection required"
        evidence.append("no pattern matched from rule-based classifier")

    return {
        "status": status,
        "failure_type": failure_type,
        "confidence": confidence,
        "evidence": evidence,
        "likely_cause": likely_cause,
        "recommended_fix": recommended_fix,
        "validation_command": validation_cmd,
        "target_agent": target_agent,
        "synthetic_only": True,
        "real_platform_logic": 0,
        "external_network": 0,
    }


def generate_outputs(result, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # diagnosis.json
    (out / "diagnosis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    # diagnosis.md
    evidence_block = "\n".join(f"- {e}" for e in result["evidence"])
    fix_block = "\n".join(f"- {f}" for f in result["recommended_fix"])
    val_block = "\n".join(f"  {v}" for v in result["validation_command"])
    md = DIAGNOSIS_TEMPLATE.format(
        status=result["status"],
        failure_type=result["failure_type"],
        confidence=result["confidence"],
        target_agent=result["target_agent"],
        evidence_block=evidence_block,
        likely_cause=result["likely_cause"],
        fix_block=fix_block,
        validation_block=val_block,
    )
    (out / "diagnosis.md").write_text(md, encoding="utf-8")

    # codex_repair_prompt.md
    prompt = CODEX_PROMPT_TEMPLATE.format(
        failure_type=result["failure_type"],
        evidence_block=evidence_block,
        likely_cause=result["likely_cause"],
        fix_block=fix_block,
        validation_block=val_block,
    )
    (out / "codex_repair_prompt.md").write_text(prompt, encoding="utf-8")

    return str(out)


def main():
    parser = argparse.ArgumentParser(description="Failure Diagnosis CLI v1")
    parser.add_argument("--input-dir", help="Directory with run_summary.json + trace.jsonl")
    parser.add_argument("--run-summary", help="Path to run_summary.json")
    parser.add_argument("--trace", help="Path to trace.jsonl")
    parser.add_argument("--failure-replay", help="Path to failure_replay.md (unused in v1)")
    parser.add_argument("--out-dir", required=True, help="Output directory for diagnosis files")
    parser.add_argument("--target-agent", default="codex", help="Target coding agent (default: codex)")
    args = parser.parse_args()

    rs, trace = load_input(
        run_summary_path=args.run_summary,
        trace_path=args.trace,
        input_dir=args.input_dir,
    )

    if not rs:
        print("No run_summary data found. Provide --run-summary or --input-dir.", file=sys.stderr)
        sys.exit(1)

    result = diagnose(rs, trace, args.target_agent)
    generate_outputs(result, args.out_dir)

    print(json.dumps(result, indent=2))
    if result["status"] == "pass":
        print("\n=== DIAGNOSIS: PASS ===")
    else:
        print(f"\n=== DIAGNOSIS: {result['failure_type']} (confidence: {result['confidence']}) ===")


if __name__ == "__main__":
    main()
