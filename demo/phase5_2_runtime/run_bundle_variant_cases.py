#!/usr/bin/env python
"""Phase 5.2-A2: Synthetic Bundle Variants.

Tests 5 synthetic JS bundles for missing-runtime behavior and full shim success.

Usage:
  python tools/phase5_2_runtime/run_bundle_variant_cases.py --out-dir outputs/phase5_2_bundle_variants --node node
"""

from __future__ import annotations

import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

# In showcase layout, assets are sibling to this script
_SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS = _SCRIPT_DIR / "assets"
BUNDLE_VAR = ASSETS / "bundle_variants"
SHIM = ASSETS / "synthetic_browser_shim.js"
ROOT = _SCRIPT_DIR.parent.parent  # showcase root, for sys.path if needed

sys.path.insert(0, str(_SCRIPT_DIR))
from runtime_error_classifier import classify_runtime_error


def run_node(node_bin, js_content, timeout=15):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js_content); tmp = f.name
    try:
        proc = subprocess.run([node_bin, tmp], capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    finally:
        try: os.unlink(tmp)
        except OSError: pass


def abs_req(path):
    return f"require('{str(path).replace(chr(92),'/')}');"


def run_failure_case(name, bundle_path, node_bin, prelude, expected_error):
    entry = f"{prelude}\n{abs_req(bundle_path)}\nconsole.log('__DONE__');"
    rc, stdout, stderr = run_node(node_bin, entry)
    cls = classify_runtime_error(stderr, stdout)
    actual = cls["error_type"]
    status = "CLASSIFIED_OK" if actual == expected_error else "MISMATCH"
    print(f"[{status}] {name}: expected={expected_error} actual={actual}")
    return {"case": name, "bundle": str(bundle_path.name), "expected_error": expected_error,
            "actual_error": actual, "status": status, "rc": rc, "stderr": stderr[:200]}


def run_success_case(name, bundle_path, node_bin):
    shim_req = abs_req(SHIM)
    bundle_req = abs_req(bundle_path)
    payload = "const payload={path:'/local/mock/signed-api',ts:3000000000000,demo_id:'bundle-test-"+name+"',nonce:'xyz789'};\n"
    sign = "const sig=window.__warb_demo_sign('/local/mock/signed-api',payload);console.log(JSON.stringify(sig));"
    entry = f"{shim_req}\n{bundle_req}\n{payload}{sign}\nconsole.log('__SIGN_DONE__');"
    rc, stdout, stderr = run_node(node_bin, entry)
    sig_result = {}
    for line in stdout.split("\n"):
        if line.strip().startswith("{") and line.strip().endswith("}"):
            try: sig_result = json.loads(line.strip()); break
            except: pass
    shim_ok = rc == 0 and bool(sig_result.get("signature"))
    mock_ok = False
    mock_reason = "no_sig"
    if shim_ok:
        try:
            from synthetic_signed_api import verify_demo_signed_request
            headers = {"x-demo-signature": sig_result.get("signature","")}
            pobj = {"path":"/local/mock/signed-api","ts":3000000000000,"demo_id":"bundle-test-"+name,"nonce":"xyz789"}
            deps = sig_result.get("dependencies",{})
            vr = verify_demo_signed_request("/local/mock/signed-api", pobj, headers, deps)
            mock_ok = vr.get("accepted",False)
            mock_reason = vr.get("reason","?")
        except Exception as e:
            mock_reason = f"err:{e}"
    status = "SUCCESS_OK" if shim_ok and mock_ok else "FAIL"
    print(f"[{status}] {name}_full_shim: shim={shim_ok} mock={mock_ok}")
    return {"case": f"{name}_full_shim", "bundle": str(bundle_path.name), "full_shim_success": shim_ok,
            "mock_api_accepted": mock_ok, "status": status, "mock_reason": mock_reason,
            "signature": sig_result.get("signature","")[:32], "rc": rc}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="outputs/phase5_2_bundle_variants")
    parser.add_argument("--node", default="node")
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    bundles = {
        "window_document": BUNDLE_VAR / "bundle_window_document_required.js",
        "navigator": BUNDLE_VAR / "bundle_navigator_required.js",
        "event_target": BUNDLE_VAR / "bundle_event_target_required.js",
        "local_storage": BUNDLE_VAR / "bundle_local_storage_required.js",
        "full_runtime": BUNDLE_VAR / "bundle_full_runtime_required.js",
    }

    # Failure cases
    # Note: Node.js v22+ has built-in navigator/EventTarget, so we must delete them
    fail_cases = [
        ("missing_window", bundles["full_runtime"], "", "missing_window"),
        ("missing_document", bundles["window_document"], "globalThis.window = globalThis;\n", "missing_document"),
        ("missing_navigator", bundles["navigator"],
         "globalThis.window=globalThis;globalThis.document={createElement:()=>({}),querySelectorAll:()=>[]};globalThis.EventTarget=class EventTarget{};globalThis.localStorage={getItem:()=>null,setItem:()=>{}};delete globalThis.navigator;\n",
         "missing_navigator"),
        ("missing_event_target", bundles["event_target"],
         "globalThis.window=globalThis;globalThis.document={createElement:()=>({}),querySelectorAll:()=>[]};globalThis.navigator={userAgent:'mock'};globalThis.localStorage={getItem:()=>null,setItem:()=>{}};delete globalThis.EventTarget;\n",
         "missing_event_target"),
        ("missing_local_storage", bundles["local_storage"],
         "globalThis.window=globalThis;globalThis.document={createElement:()=>({}),querySelectorAll:()=>[]};globalThis.navigator={userAgent:'mock'};globalThis.EventTarget=class EventTarget{};\n",
         "missing_local_storage"),
    ]

    results = []
    trace = []

    for name, bp, prelude, expected in fail_cases:
        r = run_failure_case(name, bp, args.node, prelude, expected)
        results.append(r)
        trace.append({"case": name, "status": r["status"], "expected": expected, "actual": r["actual_error"]})

    # Success cases (full shim for each bundle)
    for name, bp in bundles.items():
        r = run_success_case(name, bp, args.node)
        results.append(r)
        trace.append({"case": f"{name}_full_shim", "status": r["status"], "shim": r["full_shim_success"], "mock": r["mock_api_accepted"]})

    classified = sum(1 for r in results if r["status"]=="CLASSIFIED_OK")
    unknown = sum(1 for r in results if "MISMATCH" in r.get("status",""))
    success_count = sum(1 for r in results if r["status"]=="SUCCESS_OK")
    full_shims = sum(1 for r in results if r.get("full_shim_success"))
    mock_oks = sum(1 for r in results if r.get("mock_api_accepted"))

    summary = {
        "failure_cases": 5, "classified_failures": classified, "unknown_errors": unknown,
        "success_cases": success_count, "full_shim_success_count": full_shims,
        "mock_api_accepted_count": mock_oks, "external_network": 0, "real_platform_logic": 0,
        "synthetic_only": True,
        "overall_status": "PASS" if classified==5 and success_count==5 else "FAIL",
    }

    (out_dir/"bundle_variant_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out_dir/"bundle_variant_trace.jsonl").write_text("\n".join(json.dumps(t,ensure_ascii=False) for t in trace),encoding="utf-8")
    (out_dir/"run_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    (out_dir/"failure_replay.md").write_text("\n".join(f"## {r['case']}\n- Status: {r['status']}\n- Expected: {r.get('expected_error','')} Actual: {r.get('actual_error',r.get('mock_reason',''))}\n" for r in results),encoding="utf-8")
    (out_dir/"capability_dashboard.md").write_text(f"# Bundle Variant Dashboard\n- Failure: {classified}/{len(fail_cases)}\n- Success: {success_count}/{len(bundles)}\n- Full shim: {full_shims}\n- Mock API: {mock_oks}\n- Status: **{summary['overall_status']}**\n",encoding="utf-8")

    print(json.dumps(summary,ensure_ascii=False))
    sys.exit(0 if summary["overall_status"]=="PASS" else 1)


if __name__ == "__main__":
    main()
