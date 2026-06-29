from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


FORBIDDEN_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "ip pool",
    "account pool",
    "ban evasion",
)


def discover_runs(runs_dir: Path) -> list[Path]:
    if not runs_dir.exists():
        raise FileNotFoundError(f"runs directory not found: {runs_dir}")
    if runs_dir.is_file():
        return [runs_dir]
    children = sorted(path for path in runs_dir.iterdir() if path.is_dir() or path.is_file())
    return [path for path in children if _looks_like_run(path)]


def write_batch_report(out_dir: Path, run_summaries: list[Mapping[str, Any]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(run_summaries)
    write_json(out_dir / "summary.json", summary)
    (out_dir / "summary.md").write_text(render_summary_markdown(summary), encoding="utf-8")
    write_failures_csv(out_dir / "failures_by_type.csv", summary["failures_by_type"])
    (out_dir / "top_root_causes.md").write_text(render_top_root_causes(summary), encoding="utf-8")
    (out_dir / "repeated_failures.md").write_text(render_repeated_failures(summary), encoding="utf-8")
    (out_dir / "suggested_regression_cases.md").write_text(render_regression_cases(summary), encoding="utf-8")
    (out_dir / "repair_priority.md").write_text(render_repair_priority(summary), encoding="utf-8")
    return summary


def build_summary(run_summaries: list[Mapping[str, Any]]) -> dict[str, Any]:
    type_counter: Counter[str] = Counter()
    subtype_counter: Counter[str] = Counter()
    layer_counter: Counter[str] = Counter()
    framework_counter: Counter[str] = Counter()
    runs_by_signature: dict[str, list[dict[str, Any]]] = defaultdict(list)
    run_rows: list[dict[str, Any]] = []
    forbidden_output_count = 0

    for item in run_summaries:
        diagnosis = item.get("diagnosis", {}) if isinstance(item.get("diagnosis"), Mapping) else {}
        public = item.get("public", {}) if isinstance(item.get("public"), Mapping) else {}
        run_id = str(item.get("run_id") or item.get("name") or "unknown")
        technical = str(public.get("technical_category") or diagnosis.get("technical_category") or diagnosis.get("failure_type") or "unknown")
        subtype = str(public.get("subtype") or diagnosis.get("subtype") or "")
        layer = str(public.get("failure_layer") or diagnosis.get("failure_layer") or "unknown")
        framework = str(item.get("framework") or _framework_from_diagnosis(diagnosis) or "unknown")
        confidence = _float(public.get("confidence") or diagnosis.get("confidence") or 0.0)
        signature = f"{technical}/{subtype}"
        type_counter[technical] += 1
        subtype_counter[signature] += 1
        layer_counter[layer] += 1
        framework_counter[framework] += 1
        row = {
            "run_id": run_id,
            "source": str(item.get("source", "")),
            "technical_category": technical,
            "subtype": subtype,
            "failure_layer": layer,
            "confidence": confidence,
            "estimated_fix_difficulty": str(public.get("estimated_fix_difficulty") or "unknown"),
            "next_action": str(public.get("next_action") or ""),
            "signature": signature,
        }
        run_rows.append(row)
        runs_by_signature[signature].append(row)
        forbidden_output_count += _forbidden_count(json.dumps(item, ensure_ascii=False).lower())

    repeated = [
        {"signature": signature, "count": len(rows), "runs": [row["run_id"] for row in rows]}
        for signature, rows in sorted(runs_by_signature.items(), key=lambda pair: (-len(pair[1]), pair[0]))
        if len(rows) > 1
    ]
    repair_priority = sorted(
        run_rows,
        key=lambda row: (
            _difficulty_rank(row["estimated_fix_difficulty"]),
            -float(row["confidence"]),
            row["run_id"],
        ),
    )
    regression_cases = [
        {
            "run_id": row["run_id"],
            "technical_category": row["technical_category"],
            "subtype": row["subtype"],
            "reason": "repeated failure" if any(row["run_id"] in item["runs"] for item in repeated) else "representative failure",
        }
        for row in repair_priority[:10]
    ]
    return {
        "schema_version": "batch_diagnosis/v1",
        "total_runs": len(run_summaries),
        "diagnosed_runs": len(run_rows),
        "failures_by_type": [{"technical_category": key, "count": value} for key, value in type_counter.most_common()],
        "failures_by_subtype": [{"signature": key, "count": value} for key, value in subtype_counter.most_common()],
        "failures_by_layer": [{"failure_layer": key, "count": value} for key, value in layer_counter.most_common()],
        "failures_by_framework": [{"framework": key, "count": value} for key, value in framework_counter.most_common()],
        "repeated_failures": repeated,
        "repeated_failures_count": len(repeated),
        "suggested_regression_cases": regression_cases,
        "repair_priority": repair_priority,
        "runs": run_rows,
        "forbidden_output_count": forbidden_output_count,
    }


def write_failures_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["technical_category", "count"])
        writer.writeheader()
        for row in rows:
            writer.writerow({"technical_category": row.get("technical_category"), "count": row.get("count")})


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Batch Diagnosis Summary",
            "",
            f"- Total runs: `{summary.get('total_runs')}`",
            f"- Diagnosed runs: `{summary.get('diagnosed_runs')}`",
            f"- Repeated failure groups: `{summary.get('repeated_failures_count')}`",
            f"- Forbidden outputs: `{summary.get('forbidden_output_count')}`",
            "",
            "## Top Failure Types",
            "",
            _table(summary.get("failures_by_type", []), ("technical_category", "count")),
        ]
    )


def render_top_root_causes(summary: Mapping[str, Any]) -> str:
    return "\n".join(["# Top Root Causes", "", _table(summary.get("failures_by_type", []), ("technical_category", "count"))])


def render_repeated_failures(summary: Mapping[str, Any]) -> str:
    items = summary.get("repeated_failures", [])
    if not isinstance(items, list) or not items:
        body = "- No repeated failures detected."
    else:
        body = "\n".join(f"- `{item.get('signature')}`: {item.get('count')} runs ({', '.join(item.get('runs', []))})" for item in items if isinstance(item, Mapping))
    return "\n".join(["# Repeated Failures", "", body, ""])


def render_regression_cases(summary: Mapping[str, Any]) -> str:
    items = summary.get("suggested_regression_cases", [])
    body = "\n".join(
        f"- `{item.get('run_id')}`: {item.get('technical_category')} / {item.get('subtype')} ({item.get('reason')})"
        for item in items
        if isinstance(item, Mapping)
    ) or "- No regression cases suggested."
    return "\n".join(["# Suggested Regression Cases", "", body, ""])


def render_repair_priority(summary: Mapping[str, Any]) -> str:
    items = summary.get("repair_priority", [])
    body = "\n".join(
        f"- `{item.get('run_id')}`: {item.get('technical_category')} / {item.get('subtype')} ({item.get('estimated_fix_difficulty')}, confidence {item.get('confidence')})"
        for item in items
        if isinstance(item, Mapping)
    ) or "- No repair priority available."
    return "\n".join(["# Repair Priority", "", body, ""])


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _looks_like_run(path: Path) -> bool:
    if path.is_file():
        return True
    names = {item.name.lower() for item in path.iterdir() if item.is_file()}
    return bool(names & {"error.log", "stderr.log", "stdout.log", "console.txt", "network.json", "readme.txt", "user_description.txt"})


def _framework_from_diagnosis(diagnosis: Mapping[str, Any]) -> str:
    observations = diagnosis.get("observations")
    if isinstance(observations, Mapping):
        hint = observations.get("adapter_failure_hint")
        if isinstance(hint, Mapping) and hint.get("framework"):
            return str(hint["framework"])
    return "unknown"


def _forbidden_count(text: str) -> int:
    return sum(1 for term in FORBIDDEN_TERMS if term in text)


def _difficulty_rank(value: str) -> int:
    return {"hard": 0, "medium": 1, "easy": 2, "unknown": 3}.get(str(value).lower(), 3)


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _table(rows: Any, keys: tuple[str, str]) -> str:
    if not isinstance(rows, list) or not rows:
        return "| item | count |\n|---|---:|\n"
    first, second = keys
    lines = [f"| {first} | {second} |", "|---|---:|"]
    for row in rows:
        if isinstance(row, Mapping):
            lines.append(f"| `{row.get(first)}` | {row.get(second)} |")
    return "\n".join(lines)
