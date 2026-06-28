# Cookbook

Practical recipes for using WebAgentRuntimeBench as a developer toolkit.

## Recipe 1: Run the Full Local Smoke Test

**Goal**: Verify the entire toolkit works correctly on your machine.

**When to use**: After cloning the repo, or before making changes.

**Command**:
```powershell
cd D:\WebAgentRuntimeBench-GitHub
.\scripts\smoke_test.ps1
```

**Expected output**: `=== SMOKE TEST: PASS ===`

**What it proves**: Python + Node.js are available, safety scan passes, all A0/A2/A3 demos produce correct results, no external network needed.

**Safety**: All synthetic/local only. No external network.

---

## Recipe 2: Diagnose a Missing Runtime Object

**Goal**: Understand why a JS bundle fails outside a browser.

**When to use**: When a Node.js subprocess crashes with a ReferenceError.

**Command**:
```powershell
cd demo\phase5_2_runtime
python run_synthetic_runtime_demo.py --out-dir ..\..\sample_run\a0 --node node
```

**Expected output**: `"no_shim_success": false, "classifier_error_type": "missing_window"`

Open `sample_run\a0\trace.jsonl` to see step-by-step diagnosis.

**What it proves**: The runtime error classifier correctly identifies missing browser API objects. The repair strategy (load `synthetic_browser_shim.js`) works.

**Safety**: Synthetic only. Uses local mock values.

---

## Recipe 3: Replay a Runtime Failure

**Goal**: Step through a failure trace to understand what went wrong.

**When to use**: After running a demo, to understand each failure.

**Command**:
```powershell
cat sample_run\a2\failure_replay.md
```

**Expected output**: Table of 5 failure cases with error types, root causes, and repair steps.

**What it proves**: Failure replay documents not just errors but the repair path — making it reproducible and teachable.

**Safety**: All traces are synthetic/local.

---

## Recipe 4: Inspect Signed API Dependencies

**Goal**: Understand how a synthetic signed API's signature depends on specific inputs.

**When to use**: Before designing your own signed API verification logic.

**Command**:
```powershell
cd demo\phase5_2_runtime
python run_signed_api_benchmark.py --out-dir ..\..\sample_run\a3 --node node
cat ..\..\sample_run\a3\signed_api_trace.jsonl
```

**Expected output**: 24 trace lines covering 6 signed cases and 6 negative rejection cases.

**What it proves**: Each signed API case has a unique dependency profile (3 to 9 deps). Changing any dependency (e.g., tampering payload) causes rejection.

**Safety**: WARBDemoV2 is a synthetic algorithm. No real signatures. x-demo-signature only.

---

## Recipe 5: Use Positive/Negative Verification

**Goal**: Build confidence that a verification system catches tampering.

**When to use**: When designing signed API verification to avoid "always accepts" bugs.

**Command**: See Recipe 4's A3 trace. Inspect `negative_case_rejected` steps.

**Expected output**: All 6 tampered-payload cases produce `"accepted": false`.

**What it proves**: The verification system correctly rejects modified payloads. Without negative cases, a system that always returns "accepted" would appear to pass.

**Safety**: All verification is local mock. No real platform logic.

---

## Recipe 6: Turn a Synthetic Playwright Trace into a Repair Prompt

**Goal**: Convert a local Playwright-style `trace.zip` into `failure_artifact.json`, diagnosis reports, and an AI repair prompt.

**When to use**: Before asking a coding assistant to repair a failed Playwright run.

**Command**:
```powershell
.\scripts\adapt_smoke_test.ps1
```

**Expected output**: `=== ADAPTER SMOKE TEST: PASS ===`

**What it proves**: The `warb adapt playwright-trace --diagnose` CLI can read a sanitized local trace archive, extract status, URL, console error, failed action, exception details, snapshot reference, linked DOM excerpt, selector hints, produce an initial `selector_drift` diagnosis, and write `diagnosis.json`, `diagnosis.md`, `diagnosis_report.html`, and `repair_prompt.md`.

**Safety**: The fixture is synthetic and local. It does not launch a browser, replay network traffic, or include credentials.
