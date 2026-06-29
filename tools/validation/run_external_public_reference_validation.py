from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / "validation" / "source_ledger_external_seed_v0_9.json"
LEDGER_PATH = ROOT / "validation" / "external_public_reference_ledger.json"
HELDOUT_CASES_PATH = ROOT / "validation" / "external_heldout_20_cases.json"
HELDOUT_RESULTS_PATH = ROOT / "validation" / "external_heldout_20.json"
DOC_PATH = ROOT / "docs" / "EXTERNAL_DATA_SOURCES.md"

FORBIDDEN_OUTPUTS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "ip pool",
    "account pool",
    "绕过验证码",
    "绕过风控",
    "伪造指纹",
    "破解签名",
    "规避封禁",
)

HELDOUT_IDS = (
    "pw_10611_strict_mode",
    "pw_30069_strict_mode",
    "pw_36045_strict_or_locator",
    "so_75658146_strict_substring",
    "so_78138968_strict_multiple_locators",
    "so_76043713_strict_locator_error",
    "so_76810320_strict_four_elements",
    "bu_1913_download_not_saved",
    "bu_2046_download_not_available_next_step",
    "bu_91_download_access",
    "bu_3722_download_tracking",
    "bu_356_cloudflare_captcha",
    "bu_1582_cloudflare_patchright",
    "bu_206_omni_parser_captcha",
    "bu_3633_jenkins_blocked_captcha",
    "bu_1830_closed_pipe_windows",
    "bu_1185_windows_agent_run",
    "bu_4579_cdp_instability",
    "bu_4374_keep_alive_cdp_drop",
    "bu_4688_cdp_websocket_drops",
)

CATEGORY_TO_TECHNICAL = {
    "anti_bot_risk": "anti_bot_risk",
    "auth_permission_block": "anti_bot_risk",
    "cdp_websocket_disconnect": "cdp_websocket_disconnected",
    "dependency_conflict": "toolchain_environment",
    "download_handling": "playwright_download",
    "environment_runtime": "toolchain_environment",
    "agent_loop_or_iteration_limit": "agent_repetition_loop",
    "agent_loop_or_response_parse": "insufficient_evidence",
    "locator_timeout": "async_hydration_timing",
    "network_http_error": "anti_bot_risk",
    "route_mock_har": "playwright_route_mock_har",
    "shadow_dom_locator": "playwright_shadow_dom_locator",
    "storage_state_context": "playwright_storage_state_context",
    "strict_mode_violation": "playwright_strict_mode_violation",
    "target_closed_or_page_crash": "playwright_browser_context_closed",
    "trace_debugging": "insufficient_evidence",
    "trace_generation": "toolchain_environment",
}


def main() -> int:
    seed = load_seed()
    ledger = build_ledger(seed)
    cases = build_heldout_cases(ledger["sources"])
    results = run_heldout_cases(cases)
    heldout = summarize_heldout(cases, results)

    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    HELDOUT_CASES_PATH.write_text(json.dumps({"schema_version": "external-heldout/v0.9-cases", "cases": cases}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    HELDOUT_RESULTS_PATH.write_text(json.dumps(heldout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DOC_PATH.write_text(render_doc(ledger, heldout), encoding="utf-8")

    summary = heldout["summary"]
    print(
        "external public reference validation: "
        f"{summary['reasonable_category_match']}/{summary['total_heldout_cases']} reasonable, "
        f"{summary['actionable_next_action']}/{summary['total_heldout_cases']} actionable, "
        f"forbidden_outputs={summary['forbidden_output_count']}"
    )
    return 0 if summary["forbidden_output_count"] == 0 else 1


def load_seed() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def build_ledger(seed: dict[str, Any]) -> dict[str, Any]:
    sources = [normalize_source(item) for item in seed["sources"]]
    by_type = Counter(item["source_type"] for item in sources)
    by_category = Counter(item["category"] for item in sources)
    by_project = Counter(item["project"] for item in sources)
    return {
        "schema_version": "external-public-reference-ledger/v0.9",
        "purpose": "Traceable external public sources used to seed validation. These are not external user submissions to this repository.",
        "summary": {
            "total_sources": len(sources),
            "real_public_issue": by_type.get("real_public_issue", 0),
            "real_public_qa": by_type.get("real_public_qa", 0),
            "official_doc_pattern": by_type.get("official_doc_pattern", 0),
            "categories": dict(sorted(by_category.items())),
            "projects": dict(sorted(by_project.items())),
        },
        "sources": sources,
    }


def normalize_source(item: dict[str, Any]) -> dict[str, Any]:
    category = str(item["category"])
    source_type = str(item["source_type"])
    technical = CATEGORY_TO_TECHNICAL.get(category, "insufficient_evidence")
    validation_use = "official_doc_pattern" if source_type == "official_doc_pattern" else "external_public_reference"
    safe_boundary = str(item.get("safe_boundary", "normal_diagnostic_case"))
    title = str(item.get("title", "")).strip()
    return {
        "source_id": item["id"],
        "source_type": source_type,
        "validation_use": validation_use,
        "project": item["project"],
        "category": category,
        "source_url": item["url"],
        "title": title,
        "summary": short_summary(title, category, safe_boundary),
        "expected_diagnosis": {
            "technical_category": technical,
            "source_expected": item.get("expected", ""),
        },
        "safe_use": item.get("safe_use", "diagnosis/validation only"),
        "safe_boundary": safe_boundary,
        "can_become_validation_case": bool(item.get("can_become_validation_case")),
    }


def short_summary(title: str, category: str, safe_boundary: str) -> str:
    summary = f"{title}; category={category}; boundary={safe_boundary}"
    return summary[:237] + "..." if len(summary) > 240 else summary


def build_heldout_cases(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_by_id = {item["source_id"]: item for item in sources}
    cases = []
    for index, source_id in enumerate(HELDOUT_IDS, start=1):
        source = source_by_id[source_id]
        raw_error = raw_error_for(source)
        expected = source["expected_diagnosis"]["technical_category"]
        cases.append(
            {
                "case_id": f"EXTREF-{index:03d}",
                "source_id": source["source_id"],
                "source_url": source["source_url"],
                "source_type": source["source_type"],
                "validation_use": "external_public_reference",
                "project": source["project"],
                "category": source["category"],
                "title": source["title"],
                "input_type": "log",
                "expected_category": expected,
                "raw_error_excerpt": raw_error,
                "notes": "Sanitized short excerpt generated from a public source seed. Not a private trace and not an external user submission to this repository.",
            }
        )
    return cases


def raw_error_for(source: dict[str, Any]) -> str:
    title = source["title"]
    category = source["category"]
    if category == "strict_mode_violation":
        return f"Playwright locator.click: Error: strict mode violation: locator('button') resolved to 2 elements. Public source title: {title}"
    if category == "download_handling":
        return f"Browser agent download event fired but file was not saved; acceptDownloads is false; downloaded file not available to next step. Public source title: {title}"
    if category == "anti_bot_risk":
        return f"Browser agent reached Cloudflare challenge captcha page with verify you are human message. Public source title: {title}"
    if category == "environment_runtime":
        return f"Browser automation runtime failed on Windows; browser executable missing; playwright install needed; permission denied. Public source title: {title}"
    if category == "cdp_websocket_disconnect":
        return f"CDP WebSocket silent disconnect: httpx.ReadError while browser session is alive; connectOverCDP timeout. Public source title: {title}"
    return f"Automation failure public source title: {title}; category={category}"


def run_heldout_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="afd-extref-") as tmp:
        tmp_root = Path(tmp)
        for case in cases:
            input_dir = tmp_root / case["case_id"]
            output_dir = tmp_root / f"{case['case_id']}_report"
            input_dir.mkdir()
            (input_dir / "error.log").write_text(case["raw_error_excerpt"], encoding="utf-8")
            (input_dir / "user_description.txt").write_text(
                f"{case['title']}\nSource: {case['source_url']}\n{case['notes']}\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(output_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=30,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stdout + completed.stderr)
            diagnosis = json.loads((output_dir / "diagnosis.json").read_text(encoding="utf-8"))
            actual = str(diagnosis.get("technical_category") or diagnosis.get("failure_type") or "unknown")
            expected = str(case["expected_category"])
            forbidden_hits = forbidden_output_hits(output_dir)
            result = classify_result(expected, actual)
            results.append(
                {
                    "case_id": case["case_id"],
                    "source_id": case["source_id"],
                    "source_url": case["source_url"],
                    "validation_use": case["validation_use"],
                    "expected_category": expected,
                    "actual_category": actual,
                    "actual_subtype": diagnosis.get("subtype"),
                    "confidence": diagnosis.get("confidence"),
                    "result": result,
                    "actionable_next_action": bool(diagnosis.get("next_action") or diagnosis.get("suggested_fix")),
                    "codex_fix_prompt_generated": (output_dir / "codex_fix_prompt.md").exists(),
                    "forbidden_output_hits": forbidden_hits,
                }
            )
            shutil.rmtree(output_dir, ignore_errors=True)
    return results


def classify_result(expected: str, actual: str) -> str:
    if actual in {"unknown", "insufficient_evidence"}:
        return "insufficient_evidence"
    if actual == expected:
        return "exact_match"
    return "severe_misclassification"


def forbidden_output_hits(output_dir: Path) -> list[str]:
    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in output_dir.iterdir()
        if path.suffix.lower() in {".md", ".json", ".txt"}
    ).lower()
    return [term for term in FORBIDDEN_OUTPUTS if term.lower() in combined]


def summarize_heldout(cases: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    exact_category = sum(1 for item in results if item["result"] == "exact_match")
    reasonable = sum(1 for item in results if item["result"] in {"exact_match", "category_match"})
    actionable = sum(1 for item in results if item["actionable_next_action"])
    severe = sum(1 for item in results if item["result"] == "severe_misclassification")
    insufficient = sum(1 for item in results if item["result"] == "insufficient_evidence")
    forbidden = sum(len(item["forbidden_output_hits"]) for item in results)
    backlog = [
        {
            "case_id": item["case_id"],
            "source_id": item["source_id"],
            "expected_category": item["expected_category"],
            "actual_category": item["actual_category"],
            "result": item["result"],
        }
        for item in results
        if item["result"] in {"severe_misclassification", "insufficient_evidence"}
    ]
    return {
        "schema_version": "external-heldout/v0.9-results",
        "method": "External public reference held-out records. Sanitized summaries only; not external user submissions to this repository; not used to tune rules before first run.",
        "summary": {
            "total_heldout_cases": total,
            "reasonable_category_match": reasonable,
            "exact_category_match": exact_category,
            "exact_subtype_match": "N/A",
            "actionable_next_action": actionable,
            "severe_misclassification": severe,
            "insufficient_evidence": insufficient,
            "forbidden_output_count": forbidden,
        },
        "cases": [{**case, **result} for case, result in zip(cases, results)],
        "regression_backlog": backlog,
    }


def render_doc(ledger: dict[str, Any], heldout: dict[str, Any]) -> str:
    summary = ledger["summary"]
    held = heldout["summary"]
    return f"""# External Data Sources

This pack contains 62 external public reference seeds for Agent Failure Doctor v0.9.

These sources are not submitted to this repository by external users. They are public references and official documentation patterns used to start an external-source validation ledger.

## Source Types

| Source type | Count |
|---|---:|
| real_public_issue | {summary["real_public_issue"]} |
| real_public_qa | {summary["real_public_qa"]} |
| official_doc_pattern | {summary["official_doc_pattern"]} |

Validation use:

- `external_public_reference`: public issue or Q&A used as a traceable source seed
- `official_doc_pattern`: official documentation used as behavior boundary or correct-use reference

Do not copy long issue content into this repository. Keep only `source_url`, title, category, expected diagnosis, and a short sanitized summary.

## Held-Out 20

| Metric | Value |
|---|---:|
| Total held-out cases | {held["total_heldout_cases"]} |
| Reasonable category match | {held["reasonable_category_match"]}/{held["total_heldout_cases"]} |
| Exact category match | {held["exact_category_match"]}/{held["total_heldout_cases"]} |
| Exact subtype match | {held["exact_subtype_match"]} |
| Actionable next_action | {held["actionable_next_action"]}/{held["total_heldout_cases"]} |
| Severe misclassification | {held["severe_misclassification"]} |
| Insufficient evidence | {held["insufficient_evidence"]} |
| Forbidden output count | {held["forbidden_output_count"]} |

Safety rule: Anti-bot risk samples are identification and compliant routing only. They must not generate challenge-bypass, bot-evasion, fingerprint-spoofing, dynamic-signature-cracking, IP-pool, account-pool, or CAPTCHA-automation guidance.

## Files

- `validation/source_ledger_external_seed_v0_9.json`
- `validation/source_ledger_external_seed_v0_9.csv`
- `validation/external_public_reference_ledger.json`
- `validation/external_heldout_20_cases.json`
- `validation/external_heldout_20.json`

Reproduce:

```powershell
python -m tools.validation.run_external_public_reference_validation
```
"""


if __name__ == "__main__":
    raise SystemExit(main())
