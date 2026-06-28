# Playwright Trace Adapter v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `warb adapt playwright-trace` so it extracts structured status, URL, console/error, network, and HTML evidence from sanitized local Playwright trace archives.

**Architecture:** Keep the public adapter API as `artifact_from_playwright_trace(trace_zip, run_id=None)`. Add small private helpers in `tools/failure_artifacts/adapters.py` for JSON/JSONL event extraction and bounded network/error summaries, then exercise them through synthetic zip tests.

**Tech Stack:** Python standard library (`json`, `re`, `zipfile`, `pathlib`, `unittest`), existing `warb` CLI and failure artifact schema.

---

### Task 1: Add Red Test For Structured Playwright Trace Evidence

**Files:**
- Modify: `tests/test_failure_artifact_expansion.py`

- [x] **Step 1: Write the failing test**

Add this test method to `FailureArtifactExpansionTests`:

```python
    def test_playwright_trace_adapter_extracts_jsonl_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_zip = root / "trace.zip"
            with ZipFile(trace_zip, "w") as archive:
                archive.writestr(
                    "trace.trace",
                    "\n".join(
                        [
                            json.dumps(
                                {
                                    "type": "console",
                                    "message": {
                                        "type": "error",
                                        "text": "Timeout 30000ms waiting for selector .price",
                                    },
                                }
                            ),
                            json.dumps(
                                {
                                    "type": "event",
                                    "method": "Network.responseReceived",
                                    "params": {
                                        "response": {
                                            "url": "https://example.test/products",
                                            "status": 503,
                                            "request": {"method": "GET"},
                                        }
                                    },
                                }
                            ),
                        ]
                    ),
                )
                archive.writestr("resources/page.html", "<html><body>Service unavailable</body></html>")

            artifact = artifact_from_playwright_trace(trace_zip, run_id="pw_jsonl")

            self.assertEqual(artifact["run_id"], "pw_jsonl")
            self.assertEqual(artifact["error"]["status_code"], 503)
            self.assertEqual(artifact["observations"]["url"], "https://example.test/products")
            self.assertIn("Timeout 30000ms waiting for selector .price", artifact["error"]["message"])
            self.assertIn("Timeout 30000ms waiting for selector .price", artifact["observations"]["console_messages"])
            self.assertEqual(
                artifact["observations"]["network_events"],
                [{"method": "GET", "url": "https://example.test/products", "status": 503}],
            )
            self.assertIn("Service unavailable", artifact["observations"]["html_excerpt"])
```

- [x] **Step 2: Run the focused test to verify RED**

Run:

```powershell
python -m unittest tests.test_failure_artifact_expansion.FailureArtifactExpansionTests.test_playwright_trace_adapter_extracts_jsonl_events
```

Expected: FAIL because `observations["network_events"]` is missing or status/URL are not extracted from JSONL nested events.

### Task 2: Implement Minimal Structured Trace Parsing

**Files:**
- Modify: `tools/failure_artifacts/adapters.py`

- [x] **Step 1: Add helper extraction functions**

Add private helpers that:

- parse whole JSON objects or line-delimited JSON records,
- extract bounded console/error messages,
- extract bounded network summaries with `method`, `url`, and `status`,
- fall back safely on malformed text.

- [x] **Step 2: Wire helpers into `artifact_from_playwright_trace`**

Update the adapter to accumulate:

```python
network_events: list[dict[str, Any]] = []
```

and return it under:

```python
"network_events": network_events[:20]
```

Keep existing keys and behavior for Scrapy and requests unchanged.

- [x] **Step 3: Run the focused test to verify GREEN**

Run:

```powershell
python -m unittest tests.test_failure_artifact_expansion.FailureArtifactExpansionTests.test_playwright_trace_adapter_extracts_jsonl_events
```

Expected: PASS.

### Task 3: Add Malformed Mixed Trace Regression Test

**Files:**
- Modify: `tests/test_failure_artifact_expansion.py`

- [x] **Step 1: Write the malformed trace test**

Add a test that creates a zip containing malformed JSON, plain text with `HTTP 429`, and an HTML login marker. Assert the adapter does not crash and still extracts status plus HTML excerpt.

- [x] **Step 2: Run the malformed test**

Run:

```powershell
python -m unittest tests.test_failure_artifact_expansion.FailureArtifactExpansionTests.test_playwright_trace_adapter_handles_malformed_mixed_entries
```

Expected: PASS after Task 2 because fallback parsing handles malformed content.

### Task 4: Full Verification And Commit

**Files:**
- Modified code and tests from Tasks 1-3

- [x] **Step 1: Run focused adapter tests**

```powershell
python -m unittest tests.test_failure_artifact_expansion
```

Expected: all tests in the file pass.

- [x] **Step 2: Run all unit tests**

```powershell
python -m unittest discover -s tests -p 'test_*.py'
```

Expected: all tests pass.

- [x] **Step 3: Run smoke test**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
```

Expected: smoke test PASS.

- [x] **Step 4: Run safety scan**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

Expected: safety scan PASS.

- [x] **Step 5: Commit implementation**

```powershell
git add tools\failure_artifacts\adapters.py tests\test_failure_artifact_expansion.py docs\superpowers\plans\2026-06-28-playwright-trace-adapter-v1.md
git commit -m "feat: improve playwright trace adapter"
```
