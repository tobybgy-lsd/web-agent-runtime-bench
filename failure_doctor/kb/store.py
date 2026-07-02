from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .fingerprint import fingerprint_from_payload
from .policy import CASE_SCHEMA_VERSION, SCHEMA_VERSION, TOOL_VERSION, assess_text_safety, is_importable_safety, safe_next_action_for
from .redaction import redact_text, stable_text
from .similarity import match_case, search_score


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class KnowledgeBase:
    def __init__(self, path: Path):
        self.path = path

    def init(self) -> dict[str, Any]:
        self.path.mkdir(parents=True, exist_ok=True)
        for rel in ("cases", "indexes", "patterns", "fixes", "exports", "cache"):
            (self.path / rel).mkdir(exist_ok=True)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "created_at": now(),
            "updated_at": now(),
            "local_only": True,
            "no_upload": True,
            "sanitized_only": True,
            "case_count": 0,
            "verified_fix_count": 0,
            "regression_case_count": 0,
            "indexes": [
                "case_index.json",
                "failure_type_index.json",
                "subtype_index.json",
                "framework_index.json",
                "domain_index.json",
                "keyword_index.json",
                "fingerprint_index.json",
                "similarity_index.json",
            ],
            "safety": {
                "raw_artifacts_allowed": False,
                "private_solution_allowed": False,
                "external_sync_enabled": False,
            },
        }
        self._write_json(self.path / "kb_manifest.json", manifest)
        self._append_audit("init", {"status": "pass"})
        self.rebuild_indexes()
        return manifest

    def require(self) -> None:
        if not (self.path / "kb_manifest.json").exists():
            raise FileNotFoundError(f"KB not initialized: {self.path}")

    def status(self) -> dict[str, Any]:
        self.require()
        cases = self.list_cases()
        unsafe = [case["case_id"] for case in cases if not is_importable_safety(case.get("safety", {}))]
        missing_fp = [case["case_id"] for case in cases if not case.get("evidence_fingerprint")]
        verified = [case for case in cases if case.get("fix_status") == "verified"]
        report = {
            "schema_version": "failure_kb_health/v1",
            "status": "pass" if not unsafe and not missing_fp else "fail",
            "case_count": len(cases),
            "verified_fix_count": len(verified),
            "unsafe_case_count": len(unsafe),
            "missing_fingerprint_count": len(missing_fp),
            "external_api_call_count": 0,
            "raw_upload_count": 0,
            "private_solution_leak_count": 0,
            "forbidden_output_count": 0,
        }
        self._write_json(self.path / "kb_health_report.json", report)
        (self.path / "kb_health_report.md").write_text(
            f"# KB Health\n\nStatus: {report['status']}\n\nCases: {len(cases)}\nVerified fixes: {len(verified)}\n",
            encoding="utf-8",
        )
        return report

    def import_report(self, report: Path, *, source: str = "local_sanitized_report") -> dict[str, Any]:
        self.require()
        payload = load_report_payload(report)
        combined_text = stable_text(payload)
        safety = assess_text_safety(combined_text)
        if not is_importable_safety(safety):
            self._append_audit("import_report_blocked", {"report": str(report), "safety": safety})
            raise ValueError("report is not safe to import into the local sanitized KB")
        case_id = self._next_case_id()
        fp = fingerprint_from_payload(payload)
        failure_type = str(payload.get("failure_type") or payload.get("technical_category") or fp["failure_type"])
        subtype = str(payload.get("subtype") or fp["subtype"])
        case = {
            "schema_version": CASE_SCHEMA_VERSION,
            "case_id": case_id,
            "created_at": now(),
            "updated_at": now(),
            "source": source,
            "source_ref": str(report),
            "framework": str(payload.get("framework") or fp.get("framework") or "unknown"),
            "domain": str(payload.get("domain") or fp.get("domain") or "generic"),
            "failure_type": failure_type,
            "subtype": subtype,
            "confidence": float(payload.get("confidence") or 0.0),
            "evidence_fingerprint": fp,
            "diagnosis_summary": redact_text(_read_text(report / "diagnosis.md") or stable_text(payload), limit=1200),
            "repair_order": _repair_order_from_report(report, payload),
            "fix_status": "proposed",
            "verified_fix": {},
            "verification_summary": {},
            "safety": {k: v for k, v in safety.items() if not k.startswith("matched_")},
            "tags": [failure_type, subtype],
            "notes": [],
        }
        case_dir = self.path / "cases" / case_id
        case_dir.mkdir(parents=True)
        self._write_json(case_dir / "case.json", case)
        (case_dir / "diagnosis_summary.md").write_text(case["diagnosis_summary"], encoding="utf-8")
        self._write_json(case_dir / "evidence_fingerprint.json", fp)
        (case_dir / "fix_summary.md").write_text("\n".join(case["repair_order"]), encoding="utf-8")
        self._write_json(case_dir / "verification_summary.json", {})
        self._write_json(case_dir / "safety_metadata.json", case["safety"])
        self._append_audit("import_report", {"case_id": case_id, "report": str(report)})
        self._update_manifest_counts()
        self.rebuild_indexes()
        return case

    def import_batch(self, batch_report: Path) -> list[dict[str, Any]]:
        report_dirs = [p for p in batch_report.rglob("diagnosis.json") if p.parent != batch_report]
        imported: list[dict[str, Any]] = []
        for diagnosis in report_dirs:
            try:
                imported.append(self.import_report(diagnosis.parent, source="user_imported_sanitized"))
            except ValueError:
                continue
        return imported

    def import_ci(self, ci_report: Path) -> dict[str, Any]:
        return self.import_report(ci_report, source="ci_sanitized_artifact")

    def list_cases(self) -> list[dict[str, Any]]:
        if not (self.path / "cases").exists():
            return []
        cases: list[dict[str, Any]] = []
        for path in sorted((self.path / "cases").glob("case_*/case.json")):
            cases.append(self._read_json(path))
        return cases

    def search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        rows = []
        for case in self.list_cases():
            score = search_score(query, case)
            if score > 0:
                rows.append({"case_id": case["case_id"], "score": score, "failure_type": case.get("failure_type"), "subtype": case.get("subtype")})
        return sorted(rows, key=lambda item: item["score"], reverse=True)[:limit]

    def match_report(self, report: Path, out_dir: Path | None = None, *, limit: int = 5) -> dict[str, Any]:
        payload = load_report_payload(report)
        matches = [match_case(payload, case) for case in self.list_cases()]
        matches = [item for item in matches if item["score"] > 0]
        matches = sorted(matches, key=lambda item: item["score"], reverse=True)[:limit]
        verified = [
            {**item, "verified_fix": self.get_case(str(item["case_id"])).get("verified_fix", {})}
            for item in matches
            if item.get("verified_fix_available")
        ]
        result = {
            "schema_version": "failure_kb_match/v1",
            "generated_at": now(),
            "report": str(report),
            "matches": matches,
            "verified_fix_candidates": verified,
            "external_api_call_count": 0,
        }
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            self._write_json(out_dir / "similar_cases.json", result)
            self._write_json(out_dir / "verified_fix_candidates.json", {"candidates": verified})
            (out_dir / "similar_cases.md").write_text(render_matches_md(result), encoding="utf-8")
            (out_dir / "kb_recommendations.md").write_text(render_recommendations_md(result), encoding="utf-8")
        return result

    def get_case(self, case_id: str) -> dict[str, Any]:
        path = self.path / "cases" / case_id / "case.json"
        if not path.exists():
            raise FileNotFoundError(f"case not found: {case_id}")
        return self._read_json(path)

    def promote_fix(self, case_id: str, verification: Path) -> dict[str, Any]:
        self.require()
        case = self.get_case(case_id)
        if case.get("safety", {}).get("contains_forbidden_guidance") or case.get("safety", {}).get("contains_private_solution"):
            raise ValueError("unsafe case cannot be promoted")
        report = _load_verification(verification)
        status = str(report.get("status") or report.get("verification_status") or "unknown")
        if status not in {"resolved", "partially_resolved"}:
            raise ValueError("verification report does not prove a resolved fix")
        fix = {
            "fix_id": f"fix_{case_id.removeprefix('case_')}",
            "case_id": case_id,
            "status": "verified",
            "verified_at": now(),
            "verification_status": status,
            "fix_summary": redact_text(str(report.get("fix_summary") or "Verified by local failure-doctor verify report.")),
            "validation_commands": [redact_text(str(item), limit=200) for item in report.get("validation_commands", [])],
            "risk_level": "medium" if case.get("safety", {}).get("anti_bot_boundary") else "low",
            "do_not_apply_automatically": True,
        }
        case["fix_status"] = "verified"
        case["verified_fix"] = fix
        case["verification_summary"] = {k: v for k, v in report.items() if k != "raw"}
        case["updated_at"] = now()
        case_dir = self.path / "cases" / case_id
        self._write_json(case_dir / "case.json", case)
        self._write_json(case_dir / "verification_summary.json", case["verification_summary"])
        self._write_json(self.path / "fixes" / f"{fix['fix_id']}.json", fix)
        self._append_audit("promote_fix", {"case_id": case_id, "fix_id": fix["fix_id"]})
        self._update_manifest_counts()
        self.rebuild_indexes()
        return fix

    def mark_regression(self, case_id: str) -> dict[str, Any]:
        case = self.get_case(case_id)
        tags = set(case.get("tags", []))
        tags.add("regression")
        case["tags"] = sorted(tags)
        case["updated_at"] = now()
        self._write_json(self.path / "cases" / case_id / "case.json", case)
        self._append_audit("mark_regression", {"case_id": case_id})
        self._update_manifest_counts()
        return case

    def export_sanitized(self, out_dir: Path) -> dict[str, Any]:
        self.require()
        out_dir.mkdir(parents=True, exist_ok=True)
        cases = self.list_cases()
        export_cases = []
        fixes = []
        for case in cases:
            if case.get("safety", {}).get("shareability_decision") == "raw_local_only":
                continue
            export_case = {
                "case_id": case["case_id"],
                "source": case.get("source"),
                "framework": case.get("framework"),
                "domain": case.get("domain"),
                "failure_type": case.get("failure_type"),
                "subtype": case.get("subtype"),
                "confidence": case.get("confidence"),
                "evidence_fingerprint": case.get("evidence_fingerprint"),
                "diagnosis_summary": redact_text(str(case.get("diagnosis_summary", ""))),
                "fix_status": case.get("fix_status"),
                "safety": case.get("safety"),
                "tags": case.get("tags", []),
            }
            export_cases.append(export_case)
            if case.get("fix_status") == "verified":
                fixes.append(case.get("verified_fix", {}))
        _write_jsonl(out_dir / "cases.jsonl", export_cases)
        _write_jsonl(out_dir / "fixes.jsonl", fixes)
        _write_jsonl(out_dir / "patterns.jsonl", _patterns_from_cases(cases))
        stats = {"case_count": len(export_cases), "verified_fix_count": len(fixes), "external_api_call_count": 0}
        self._write_json(out_dir / "stats.json", stats)
        manifest = {
            "schema_version": "failure_kb_export/v1",
            "generated_at": now(),
            "sanitized_only": True,
            "raw_secret_in_export": 0,
            "private_solution_in_export": 0,
            **stats,
        }
        self._write_json(out_dir / "kb_export_manifest.json", manifest)
        (out_dir / "README.md").write_text(
            "# Sanitized Failure Knowledge Base Export\n\nThis export contains summaries and fingerprints only.\n",
            encoding="utf-8",
        )
        self._append_audit("export_sanitized", {"out": str(out_dir), "case_count": len(export_cases)})
        return manifest

    def rebuild_indexes(self) -> dict[str, Any]:
        (self.path / "indexes").mkdir(parents=True, exist_ok=True)
        cases = self.list_cases()
        case_index = {
            "schema_version": "failure_kb_index/v1",
            "updated_at": now(),
            "cases": [
                {
                    "case_id": case["case_id"],
                    "failure_type": case.get("failure_type"),
                    "subtype": case.get("subtype"),
                    "framework": case.get("framework"),
                    "domain": case.get("domain"),
                    "fix_status": case.get("fix_status"),
                }
                for case in cases
            ],
        }
        self._write_json(self.path / "indexes" / "case_index.json", case_index)
        for field, filename in (
            ("failure_type", "failure_type_index.json"),
            ("subtype", "subtype_index.json"),
            ("framework", "framework_index.json"),
            ("domain", "domain_index.json"),
        ):
            index: dict[str, list[str]] = {}
            for case in cases:
                index.setdefault(str(case.get(field, "unknown")), []).append(case["case_id"])
            self._write_json(self.path / "indexes" / filename, index)
        fingerprint_index = {case["case_id"]: case.get("evidence_fingerprint", {}) for case in cases}
        self._write_json(self.path / "indexes" / "fingerprint_index.json", fingerprint_index)
        self._write_json(self.path / "indexes" / "similarity_index.json", case_index)
        self._write_json(self.path / "indexes" / "keyword_index.json", _keyword_index(cases))
        return case_index

    def _next_case_id(self) -> str:
        numbers = []
        for case in self.list_cases():
            try:
                numbers.append(int(str(case["case_id"]).split("_")[-1]))
            except Exception:
                continue
        return f"case_{(max(numbers) if numbers else 0) + 1:06d}"

    def _update_manifest_counts(self) -> None:
        manifest = self._read_json(self.path / "kb_manifest.json")
        cases = self.list_cases()
        manifest["updated_at"] = now()
        manifest["case_count"] = len(cases)
        manifest["verified_fix_count"] = sum(1 for case in cases if case.get("fix_status") == "verified")
        manifest["regression_case_count"] = sum(1 for case in cases if "regression" in case.get("tags", []))
        self._write_json(self.path / "kb_manifest.json", manifest)

    def _append_audit(self, action: str, payload: dict[str, Any]) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        with (self.path / "audit_log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"at": now(), "action": action, "payload": payload}, ensure_ascii=False) + "\n")

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_report_payload(report: Path) -> dict[str, Any]:
    if report.is_file():
        return json.loads(report.read_text(encoding="utf-8")) if report.suffix == ".json" else {"text": report.read_text(encoding="utf-8", errors="replace")}
    diagnosis_path = report / "diagnosis.json"
    if not diagnosis_path.exists():
        ci_path = report / "ci_summary.json"
        if ci_path.exists():
            payload = json.loads(ci_path.read_text(encoding="utf-8"))
            return payload.get("diagnosis", payload)
        raise FileNotFoundError(f"diagnosis.json not found in report: {report}")
    payload = json.loads(diagnosis_path.read_text(encoding="utf-8"))
    payload.setdefault("diagnosis_summary", _read_text(report / "diagnosis.md"))
    payload.setdefault("repair_suggestions", _read_text(report / "repair_suggestions.md"))
    return payload


def render_matches_md(result: dict[str, Any]) -> str:
    lines = ["# Similar Historical Failures", ""]
    if not result.get("matches"):
        lines.append("No similar local KB case found.")
    for item in result.get("matches", []):
        lines.extend(
            [
                f"## {item['case_id']}",
                "",
                f"- Score: {item['score']}",
                f"- Type: {item.get('failure_type')} / {item.get('subtype')}",
                f"- Verified fix available: {item.get('verified_fix_available')}",
                f"- Matched dimensions: {', '.join(item.get('matched_dimensions', []))}",
                f"- Why: {item.get('why_matched')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_recommendations_md(result: dict[str, Any]) -> str:
    lines = ["# KB Recommendations", ""]
    if not result.get("matches"):
        lines.append("No local historical match. Continue normal diagnosis.")
    for item in result.get("matches", [])[:5]:
        lines.extend(
            [
                f"- `{item['case_id']}` score `{item['score']}`: use as an evidence-backed suggestion only; do not auto-apply.",
            ]
        )
    if result.get("verified_fix_candidates"):
        lines.append("")
        lines.append("Verified fix candidates exist, but still require human review and local verification.")
    return "\n".join(lines).rstrip() + "\n"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _repair_order_from_report(report: Path, payload: dict[str, Any]) -> list[str]:
    text = _read_text(report / "repair_suggestions.md") or str(payload.get("next_action") or "")
    safe = safe_next_action_for(str(payload.get("failure_type") or payload.get("technical_category")), str(payload.get("subtype")), text)
    return [redact_text(safe, limit=500)]


def _load_verification(path: Path) -> dict[str, Any]:
    candidate = path / "verification_report.json" if path.is_dir() else path
    if not candidate.exists():
        raise FileNotFoundError(f"verification report not found: {path}")
    return json.loads(candidate.read_text(encoding="utf-8"))


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _patterns_from_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = {}
    for case in cases:
        key = f"{case.get('failure_type')}::{case.get('subtype')}"
        seen.setdefault(key, {"pattern": key, "case_count": 0})
        seen[key]["case_count"] += 1
    return list(seen.values())


def _keyword_index(cases: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for case in cases:
        for token in case.get("evidence_fingerprint", {}).get("tokens", [])[:40]:
            index.setdefault(token, []).append(case["case_id"])
    return index
