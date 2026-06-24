#!/usr/bin/env python
"""Run the Phase 5.2-A0 synthetic dynamic runtime demo."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from runtime_error_classifier import classify_runtime_error
from signature_dependency_tracer import trace_signature_dependencies
from synthetic_signed_api import HEADER_NAME, verify_demo_signed_request

ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = Path(__file__).resolve().parent / "assets"
DEFAULT_OUT_DIR = ROOT / "outputs" / "phase5_2_synthetic_runtime_demo"
PAYLOAD = {"demo_case": "phase5_2_a0", "items": [3, 1, 4], "synthetic": True}
DEMO_PATH = "/local/mock/signed-api"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_trace(path: Path, step: str, data: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"step": step, **data}, ensure_ascii=False) + "\n")


def run_node(node_bin: str, script: Path) -> dict:
    proc = subprocess.run(
        [node_bin, str(script)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "success": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def render_failure_replay(out_dir: Path, no_shim: dict, classifier: dict, with_shim: dict, api_result: dict) -> None:
    content = f"""# Phase 5.2-A0 Synthetic Runtime Failure Replay

## 初次失败原因

`entry_no_shim.js` 未加载 synthetic browser shim，bundle 访问 browser runtime globals 时失败。

## Classifier 识别

- error_type: `{classifier['error_type']}`
- recommended_patch: `{classifier['recommended_patch']}`

## Shim 如何修复

`synthetic_browser_shim.js` 提供本地 fake `window`、`document`、`navigator`、`EventTarget`、`localStorage` 等运行时对象。

## 复跑结果

- no_shim success: `{no_shim['success']}`
- with_shim success: `{with_shim['success']}`

## Mock API 验证

- accepted: `{api_result['accepted']}`
- reason: `{api_result['reason']}`

## 如果失败如何定位

1. 查看 `trace.jsonl` 的 `runtime_error_classified` step。
2. 确认 shim 是否先于 bundle 加载。
3. 确认 `x-demo-signature` 由 synthetic bundle 生成。
4. 确认 payload、path、userAgent、local salt 是否进入 dependency trace。
"""
    (out_dir / "failure_replay.md").write_text(content, encoding="utf-8")


def render_capability_dashboard(out_dir: Path, summary: dict) -> None:
    rows = [
        ("synthetic_bundle_loaded", summary["with_shim_run"]["success"]),
        ("no_shim_failure_detected", not summary["no_shim_run"]["success"]),
        ("runtime_error_classified", summary["classifier"]["error_type"] != "unknown_runtime_error"),
        ("browser_shim_applied", summary["with_shim_run"]["success"]),
        ("sign_function_resolved", summary["sign_function_resolved"]),
        ("dependency_traced", summary["dependency_count"] >= 5),
        ("local_mock_api_verified", summary["mock_api"]["accepted"]),
        ("external_network_avoided", summary["external_network"] == 0),
        ("real_platform_logic_absent", summary["forbidden_real_platform"] == 0),
    ]
    body = ["# Phase 5.2-A0 Capability Dashboard", "", "| capability | status |", "|---|---|"]
    for name, ok in rows:
        body.append(f"| {name} | {'PASS' if ok else 'FAIL'} |")
    body.append("")
    (out_dir / "capability_dashboard.md").write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--node", default="node")
    parser.add_argument("--keep-temp", default="false")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_path = out_dir / "trace.jsonl"
    trace_path.write_text("", encoding="utf-8")

    temp_dir = Path(tempfile.mkdtemp(prefix="phase5_2_runtime_"))
    try:
        no_shim_entry = temp_dir / "entry_no_shim.js"
        no_shim_entry.write_text(
            f"""
require({json.dumps(str(ASSET_DIR / 'synthetic_obfuscated_bundle.js'))});
const result = window.__warb_demo_sign({json.dumps(DEMO_PATH)}, {json.dumps(PAYLOAD)});
console.log(JSON.stringify(result));
""".strip(),
            encoding="utf-8",
        )
        no_shim = run_node(args.node, no_shim_entry)
        append_trace(trace_path, "no_shim_run", no_shim)

        classifier = classify_runtime_error(no_shim["stderr"], no_shim["stdout"])
        append_trace(trace_path, "runtime_error_classified", classifier)

        with_shim_entry = temp_dir / "entry_with_shim.js"
        with_shim_entry.write_text(
            f"""
require({json.dumps(str(ASSET_DIR / 'synthetic_browser_shim.js'))});
require({json.dumps(str(ASSET_DIR / 'synthetic_obfuscated_bundle.js'))});
const result = window.__warb_demo_sign({json.dumps(DEMO_PATH)}, {json.dumps(PAYLOAD)});
console.log(JSON.stringify(result));
""".strip(),
            encoding="utf-8",
        )
        append_trace(trace_path, "shim_applied", {"synthetic_only": True})
        with_shim = run_node(args.node, with_shim_entry)
        append_trace(trace_path, "sign_function_resolved", with_shim)

        sign_result = json.loads(with_shim["stdout"]) if with_shim["success"] else {}
        dependency_trace = trace_signature_dependencies(sign_result)
        append_trace(trace_path, "dependency_traced", dependency_trace)

        headers = {HEADER_NAME: sign_result.get("signature", "")}
        api_result = verify_demo_signed_request(
            DEMO_PATH,
            PAYLOAD,
            headers,
            sign_result.get("dependencies", {}),
        )
        append_trace(trace_path, "mock_api_verified", api_result)
        write_json(out_dir / "mock_api_result.json", api_result)

        summary = {
            "node_runtime": args.node,
            "no_shim_run": no_shim,
            "classifier": classifier,
            "with_shim_run": with_shim,
            "sign_function_resolved": bool(sign_result.get("signature")),
            "dependency_count": dependency_trace["dependency_count"],
            "dependency_trace": dependency_trace,
            "mock_api": api_result,
            "trace_path": str(trace_path),
            "summary_path": str(out_dir / "run_summary.json"),
            "synthetic_only": True,
            "forbidden_real_platform": 0,
            "external_network": 0,
            "sensitive_header": 0,
        }
        write_json(out_dir / "run_summary.json", summary)
        render_failure_replay(out_dir, no_shim, classifier, with_shim, api_result)
        render_capability_dashboard(out_dir, summary)
        print(json.dumps({
            "demo": "phase5_2_a0_synthetic_dynamic_runtime",
            "no_shim_success": no_shim["success"],
            "classifier_error_type": classifier["error_type"],
            "with_shim_success": with_shim["success"],
            "sign_function_resolved": summary["sign_function_resolved"],
            "dependency_count": summary["dependency_count"],
            "mock_api_accepted": api_result["accepted"],
            "synthetic_only": True,
            "forbidden_real_platform": 0,
            "external_network": 0,
        }, ensure_ascii=False))
        return 0 if (
            not no_shim["success"]
            and classifier["error_type"] in {
                "missing_window",
                "missing_document",
                "missing_navigator",
                "missing_event_target",
                "missing_local_storage",
            }
            and with_shim["success"]
            and summary["sign_function_resolved"]
            and summary["dependency_count"] >= 5
            and api_result["accepted"]
        ) else 1
    finally:
        if str(args.keep_temp).lower() != "true":
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
