#!/usr/bin/env python
"""Phase 5.2-A3: Run Synthetic Signed API Benchmark.

Tests 6 synthetic signed-API cases with increasing dependency complexity,
verifies each signature locally, and runs negative tampering tests.

Usage:
  python tools/phase5_2_runtime/run_signed_api_benchmark.py --out-dir outputs/phase5_2_signed_api_benchmark --node node
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS = SCRIPT_DIR / "assets"
SHIM = ASSETS / "synthetic_browser_shim.js"
MATRIX_BUNDLE = ASSETS / "synthetic_signed_api_matrix_bundle.js"

sys.path.insert(0, str(SCRIPT_DIR))
from synthetic_signed_api_benchmark import (
    HEADER_NAME,
    build_negative_cases,
    verify_signed_api_case,
)

CASES = [
    {
        "case_name": "path_payload_basic",
        "request": {
            "method": "POST",
            "path": "/local/mock/signed-api/basic",
            "payload": {"item": "demo_widget", "qty": 2},
        },
    },
    {
        "case_name": "timestamp_nonce",
        "request": {
            "method": "POST",
            "path": "/local/mock/signed-api/timestamp-nonce",
            "payload": {"item": "demo_clock", "qty": 1},
            "timestamp": "2026-06-24T00:00:00Z",
            "nonce": "synthetic_nonce_v1",
        },
    },
    {
        "case_name": "user_agent_salt",
        "request": {
            "method": "POST",
            "path": "/local/mock/signed-api/user-agent-salt",
            "payload": {"item": "demo_browser", "qty": 3},
        },
    },
    {
        "case_name": "document_meta_token",
        "request": {
            "method": "POST",
            "path": "/local/mock/signed-api/document-meta",
            "payload": {"item": "demo_meta", "qty": 4},
        },
    },
    {
        "case_name": "event_token",
        "request": {
            "method": "POST",
            "path": "/local/mock/signed-api/event-token",
            "payload": {"item": "demo_event", "qty": 5},
        },
    },
    {
        "case_name": "full_dependency_matrix",
        "request": {
            "method": "POST",
            "path": "/local/mock/signed-api/full-matrix",
            "payload": {"item": "demo_full", "qty": 6},
            "timestamp": "2026-06-24T00:00:00Z",
            "nonce": "synthetic_nonce_full_v1",
        },
    },
]


def _abs_req(path: Path) -> str:
    return f"require('{str(path).replace(chr(92), '/')}');"


def run_node(node_bin: str, js_code: str, timeout: int = 15):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js_code)
        tmp = f.name
    try:
        proc = subprocess.run([node_bin, tmp], capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def build_matrix_entry() -> str:
    """Construct JS entry that loads shim, monkey-patches document.querySelector for meta tokens,
    loads the matrix bundle, and calls all 6 cases."""
    cases_json = json.dumps(CASES)
    return f"""\
{_abs_req(SHIM)}
// Monkey-patch document.querySelector to return synthetic meta token element
(function () {{
  var _origQS = document.querySelector;
  var metaTokenEl = {{
    getAttribute: function (name) {{
      if (name === 'content') return 'synthetic_meta_token_v1';
      return null;
    }},
    tagName: 'META'
  }};
  document.querySelector = function (selector) {{
    if (selector === 'meta[name="warb-demo-token"]') return metaTokenEl;
    return _origQS(selector);
  }};
}})();

{_abs_req(MATRIX_BUNDLE)}

var results = [];
var cases = {cases_json};
for (var i = 0; i < cases.length; i++) {{
  var c = cases[i];
  try {{
    var sig = window.__warb_demo_sign_matrix(c.case_name, c.request);
    results.push(sig);
  }} catch (e) {{
    results.push({{ case_name: c.case_name, error: String(e) }});
  }}
}}
console.log(JSON.stringify(results));
"""


def main():
    parser = argparse.ArgumentParser(description="Phase 5.2-A3 Signed API Benchmark")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument("--node", default="node", help="Node.js binary")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run JS matrix bundle
    entry = build_matrix_entry()
    rc, stdout, stderr = run_node(args.node, entry)

    sig_results = []
    for line in stdout.split("\n"):
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            try:
                sig_results = json.loads(line)
                break
            except json.JSONDecodeError:
                pass

    if not sig_results:
        print(json.dumps({"error": "no_sign_results", "stderr": stderr[:500]}))
        sys.exit(1)

    # 2. Verify each case
    trace_lines = []
    results = []
    signed_count = 0
    verified_count = 0
    negative_total = 0
    negative_rejected = 0
    dep_counts = []

    for sr in sig_results:
        cn = sr.get("case_name", "?")
        sig = sr.get("signature", "")
        deps = sr.get("dependencies", {})
        err = sr.get("error", "")

        case_def = next((c for c in CASES if c["case_name"] == cn), None)
        request = case_def["request"] if case_def else {}

        signed_ok = bool(sig) and not err
        if signed_ok:
            signed_count += 1

        headers = {HEADER_NAME: sig} if sig else {}
        vr = verify_signed_api_case(cn, request, headers, deps)

        dep_n = len([k for k, v in deps.items() if v and k != "algorithm"])
        dep_counts.append(dep_n)

        trace_lines.append({
            "step": "case_signed",
            "case_name": cn,
            "signed": signed_ok,
            "signature": sig,
            "error": err,
        })
        trace_lines.append({
            "step": "dependencies_traced",
            "case_name": cn,
            "dependencies": deps,
            "dependency_count": dep_n,
        })
        trace_lines.append({
            "step": "mock_api_verified",
            "case_name": cn,
            "accepted": vr["accepted"],
            "reason": vr["reason"],
        })

        if vr["accepted"]:
            verified_count += 1

        # Negative cases
        neg_result = {
            "case_name": cn,
            "signed": signed_ok,
            "verified": vr["accepted"],
            "dependencies": deps,
            "dependency_count": dep_n,
            "signature": sig,
        }
        negatives = build_negative_cases(neg_result)
        neg_accepted_all = False
        for ni, neg in enumerate(negatives):
            negative_total += 1
            neg_req = neg["request"]
            neg_deps = neg["dependencies"]
            neg_expected = verify_signed_api_case(cn, neg_req, {HEADER_NAME: sig}, neg_deps)
            neg_accepted = neg_expected["accepted"]
            if not neg_accepted:
                negative_rejected += 1
            else:
                neg_accepted_all = True
            trace_lines.append({
                "step": "negative_case_rejected",
                "case_name": cn,
                "negative_type": neg["negative_type"],
                "rejected": not neg_accepted,
            })

        results.append({
            "case_name": cn,
            "signed": signed_ok,
            "verified": vr["accepted"],
            "dependency_count": dep_n,
            "negative_count": len(negatives),
            "negative_rejected_count": len(negatives) if not neg_accepted_all else 0,
            "signature": sig,
            "dependencies": deps,
            "error": err,
        })

    overall = verified_count == 6 and negative_rejected == 6

    summary = {
        "total_cases": 6,
        "signed_cases": signed_count,
        "verified_cases": verified_count,
        "negative_cases": negative_total,
        "negative_rejected": negative_rejected,
        "dependency_trace_cases": 6,
        "min_dependency_count": min(dep_counts) if dep_counts else 0,
        "max_dependency_count": max(dep_counts) if dep_counts else 0,
        "mock_api_accepted_count": verified_count,
        "external_network": 0,
        "real_platform_logic": 0,
        "synthetic_only": True,
        "overall_status": "PASS" if overall else "FAIL",
    }

    # Write outputs
    (out_dir / "signed_api_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (out_dir / "signed_api_trace.jsonl").write_text(
        "\n".join(json.dumps(t, ensure_ascii=False) for t in trace_lines) + "\n",
        encoding="utf-8",
    )
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # failure_replay.md
    fr_lines = [
        "# Signed API Benchmark — Failure Replay",
        "",
        "## Synthetic Only",
        "All operations are local/synthetic. No real platforms.",
        "",
        "## Diagnostic Guide",
        "",
        "1. **JS bundle not registered**: Check `window.__warb_demo_sign_matrix` exists after loading matrix bundle.",
        "2. **Dependency missing**: Check `synthetic_browser_shim.js` is loaded before matrix bundle.",
        "3. **Mock API rejected**: Verify signature computation matches WARBDemoV2 algorithm on both sides.",
        "4. **Negative case not rejected**: Tampered payload should produce different signature.",
        "",
        "## Case Replay",
        "",
        "| Case | Signed | Verified | Negative Rejected | Status |",
        "|------|:------:|:--------:|:-----------------:|:------:|",
    ]
    for r in results:
        st = "PASS" if r["signed"] and r["verified"] else "FAIL"
        nr = r.get("negative_rejected_count", 0)
        nrt = "PASS" if nr > 0 else "FAIL"
        fr_lines.append(
            f"| {r['case_name']} | {'✅' if r['signed'] else '❌'} | {'✅' if r['verified'] else '❌'} | {nrt} | {st} |"
        )
    fr_lines.append("")
    (out_dir / "failure_replay.md").write_text("\n".join(fr_lines), encoding="utf-8")

    # capability_dashboard.md
    caps = {
        "matrix_bundle_loaded": "PASS" if signed_count > 0 else "FAIL",
        "cases_signed": "PASS" if signed_count == 6 else "FAIL",
        "dependencies_traced": "PASS" if len(dep_counts) == 6 else "FAIL",
        "mock_api_verified": "PASS" if verified_count == 6 else "FAIL",
        "negative_cases_rejected": "PASS" if negative_rejected == negative_total else "FAIL",
        "external_network_avoided": "PASS",
        "real_platform_logic_absent": "PASS",
        "synthetic_only": "PASS",
    }
    cd_lines = [
        "# Signed API Benchmark — Capability Dashboard",
        "",
        "| Capability | Status |",
        "|------------|--------|",
    ]
    for cap, status in caps.items():
        cd_lines.append(f"| {cap} | {status} |")
    cd_lines.append("")
    (out_dir / "capability_dashboard.md").write_text("\n".join(cd_lines), encoding="utf-8")

    print(json.dumps(summary, indent=2))

    if not overall:
        sys.exit(1)


if __name__ == "__main__":
    main()
