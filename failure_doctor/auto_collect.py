from __future__ import annotations

import fnmatch
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from zipfile import ZIP_DEFLATED, ZipFile

from failure_doctor.ai_handoff import write_ai_handoff_pack
from failure_doctor.sanitize_share import sanitize_failure_pack
from tools.failure_artifacts.resolution import generate_fix_plan, render_fix_plan_markdown, write_json


COLLECTOR_VERSION = "3.2.0"
MANIFEST_SCHEMA = "collection_manifest/v1"
SUPPORTED_PRESETS = {
    "auto",
    "playwright",
    "selenium",
    "scrapy",
    "requests_httpx",
    "node_browser",
    "generic_rpa",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

BROWSER_PROFILE_DIRS = {
    "default",
    "profile",
    "user data",
    "user-data",
    "chrome profile",
    "firefox profile",
}

SENSITIVE_NAMES = {
    "cookies",
    "cookies-journal",
    "login data",
    "web data",
    "id_rsa",
    "id_ed25519",
    "known_hosts",
}

COLLECTABLE_EXTENSIONS = {
    ".log",
    ".txt",
    ".json",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".webm",
    ".html",
    ".htm",
    ".csv",
    ".xml",
    ".cfg",
    ".ini",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".js",
    ".ts",
}

FAILURE_MARKERS = {
    "timeouterror",
    "nosuchelement",
    "strict mode violation",
    "err_proxy",
    "err_name_not_resolved",
    "err_cert",
    "traceback",
    "exception",
    "failed",
    "failure",
    "http 401",
    "http 403",
    "http 429",
    "captcha",
    "verify you are human",
    "proxy_connection_failed",
}


def collect_project(
    project: Path,
    out_dir: Path,
    *,
    preset: str = "auto",
    dry_run: bool = False,
    auto_diagnose: bool = False,
    auto_handoff: bool = False,
    auto_sanitize: bool = False,
    open_report: bool = False,
    broad_scope: bool = False,
    include_hidden: bool = False,
    max_file_mb: int = 50,
    max_total_mb: int = 500,
) -> dict[str, Any]:
    project = project.resolve()
    out_dir = out_dir.resolve()
    if preset not in SUPPORTED_PRESETS:
        raise ValueError(f"unsupported preset: {preset}")
    if not project.exists() or not project.is_dir():
        raise FileNotFoundError(f"project not found: {project}")
    if not broad_scope and _looks_like_broad_scope(project):
        raise ValueError("refusing broad project scope; choose a concrete project folder")
    source_files = [
        source
        for source in _iter_project_files(project, include_hidden=include_hidden)
        if source != out_dir and out_dir not in source.parents
    ]

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw_local_only_do_not_share"
    sanitized_dir = out_dir / "sanitized_failure_pack"
    if not dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)

    frameworks = detect_frameworks(project, preset)
    copied_files: list[dict[str, Any]] = []
    skipped_files: list[dict[str, Any]] = []
    total_bytes = 0

    for source in source_files:
        relative = source.relative_to(project).as_posix()
        skip_reason = _skip_reason(project, source, include_hidden=include_hidden)
        if skip_reason:
            skipped_files.append({"relative_path": relative, "reason": skip_reason})
            continue
        size = source.stat().st_size
        if size > max_file_mb * 1024 * 1024:
            skipped_files.append({"relative_path": relative, "reason": "file_too_large"})
            continue
        if total_bytes + size > max_total_mb * 1024 * 1024:
            skipped_files.append({"relative_path": relative, "reason": "total_size_limit"})
            continue
        if not _is_collectable(source):
            skipped_files.append({"relative_path": relative, "reason": "unsupported_file_type"})
            continue
        total_bytes += size
        target = raw_dir / relative
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        copied_files.append(
            {
                "source_path": str(source),
                "relative_path": relative,
                "copied_to": str(target) if not dry_run else None,
                "kind": _kind_for(source),
                "size_bytes": size,
                "sha256": _sha256(source),
                "sanitized": False,
                "redaction_report": None,
                "included": True,
                "reason": "matched_collector_rules",
            }
        )

    signals = _detect_failure_signals(project, copied_files)
    if not signals:
        signals = ["no_failure_signal_found"]

    redaction_report: dict[str, Any] = {"total_redactions": 0, "categories": {}}
    if dry_run:
        sanitized_dir.mkdir(parents=True, exist_ok=True)
        (sanitized_dir / "README_FOR_REVIEWER.md").write_text("Dry run: no files were copied.\n", encoding="utf-8")
    else:
        sanitize_result = sanitize_failure_pack(raw_dir, sanitized_dir)
        redaction_report = dict(sanitize_result.get("redaction_report", {}))

    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project),
        "output_dir": str(out_dir),
        "collector_version": COLLECTOR_VERSION,
        "preset": preset,
        "dry_run": dry_run,
        "scope": {
            "allowed_root": str(project),
            "broad_scope": broad_scope,
            "include_hidden": include_hidden,
            "max_file_mb": max_file_mb,
            "max_total_mb": max_total_mb,
        },
        "files": copied_files,
        "skipped_files": skipped_files,
        "detected_frameworks": frameworks,
        "detected_failure_signals": signals,
        "safety": {
            "local_only": True,
            "no_external_upload": True,
            "no_browser_profile_access": True,
            "contains_credentials": _contains_credentials(redaction_report),
            "sanitized_before_share": True,
        },
        "pipeline": {
            "auto_diagnose": auto_diagnose,
            "auto_handoff": auto_handoff,
            "auto_sanitize": auto_sanitize or True,
            "open_report": open_report,
        },
    }

    _write_json(out_dir / "collection_manifest.json", manifest)
    (out_dir / "collection_summary.md").write_text(_render_collection_summary(manifest), encoding="utf-8")
    (out_dir / "open_this_first.md").write_text(_render_open_first(manifest), encoding="utf-8")

    if auto_diagnose:
        _run_diagnosis_pipeline(sanitized_dir, out_dir)
    elif "no_failure_signal_found" in signals:
        _write_no_failure_report(out_dir)

    if auto_handoff and (out_dir / "report" / "diagnosis.json").exists():
        write_ai_handoff_pack(out_dir / "report", out_dir / "ai_handoff", target="all")

    return manifest


def detect_frameworks(project: Path, preset: str = "auto") -> list[str]:
    if preset != "auto":
        return [preset]
    names = {path.name.lower() for path in project.iterdir()}
    text_blobs = _read_small_texts(project, limit=20)
    joined = "\n".join(text_blobs).lower()
    frameworks: list[str] = []
    if "playwright.config" in " ".join(names) or "playwright" in joined:
        frameworks.append("playwright")
    if "selenium" in joined or any("selenium" in name or "chromedriver" in name or "geckodriver" in name for name in names):
        frameworks.append("selenium")
    if "scrapy.cfg" in names or "scrapy" in joined:
        frameworks.append("scrapy")
    if "requests" in joined or "httpx" in joined:
        frameworks.append("requests_httpx")
    if "puppeteer" in joined or "cypress" in joined:
        frameworks.append("node_browser")
    if "rpa" in joined or "robot" in joined or "steps" in joined:
        frameworks.append("generic_rpa")
    return frameworks or ["generic_rpa"]


def watch_project_once(
    project: Path,
    out_dir: Path,
    *,
    preset: str = "auto",
    auto_diagnose: bool = False,
    auto_handoff: bool = False,
    auto_sanitize: bool = False,
    ignore: str = "",
) -> dict[str, Any]:
    project = project.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events = []
    ignore_patterns = [item.strip() for item in ignore.split(",") if item.strip()]
    for path in _iter_project_files(project, include_hidden=False):
        rel = path.relative_to(project).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) or rel.startswith(pattern.rstrip("/") + "/") for pattern in ignore_patterns):
            continue
        if _skip_reason(project, path, include_hidden=False):
            continue
        if _is_collectable(path):
            events.append({"event": "seen", "relative_path": rel, "size_bytes": path.stat().st_size})
    events_path = out_dir / "watch_events.jsonl"
    events_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in events) + ("\n" if events else ""), encoding="utf-8")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / "runs" / run_id
    collect_project(
        project,
        run_dir,
        preset=preset,
        auto_diagnose=auto_diagnose,
        auto_handoff=auto_handoff,
        auto_sanitize=auto_sanitize,
    )
    summary = {"schema_version": "watch_summary/v1", "events_seen": len(events), "runs_created": 1, "latest_run": str(run_dir)}
    _write_json(out_dir / "watch_summary.json", summary)
    (out_dir / "watch_summary.md").write_text(
        f"# Watch Summary\n\n- Events seen: `{len(events)}`\n- Latest run: `{run_dir}`\n",
        encoding="utf-8",
    )
    return summary


def watch_project(
    project: Path,
    out_dir: Path,
    *,
    preset: str = "auto",
    auto_diagnose: bool = False,
    auto_handoff: bool = False,
    auto_sanitize: bool = False,
    debounce_seconds: float = 5.0,
    max_events: int = 100,
    once: bool = False,
    poll_interval: float = 2.0,
    ignore: str = "",
) -> dict[str, Any]:
    if once:
        return watch_project_once(
            project,
            out_dir,
            preset=preset,
            auto_diagnose=auto_diagnose,
            auto_handoff=auto_handoff,
            auto_sanitize=auto_sanitize,
            ignore=ignore,
        )
    seen: set[tuple[str, int]] = set()
    events = 0
    while events < max_events:
        snapshot = _snapshot(project, ignore=ignore)
        new_items = [item for item in snapshot if item not in seen]
        if new_items:
            time.sleep(debounce_seconds)
            return watch_project_once(
                project,
                out_dir,
                preset=preset,
                auto_diagnose=auto_diagnose,
                auto_handoff=auto_handoff,
                auto_sanitize=auto_sanitize,
                ignore=ignore,
            )
        seen.update(snapshot)
        events += 1
        time.sleep(poll_interval)
    return {"schema_version": "watch_summary/v1", "events_seen": 0, "runs_created": 0, "latest_run": None}


def _run_diagnosis_pipeline(input_dir: Path, out_dir: Path) -> None:
    from failure_doctor.cli import diagnose_inputs, plan_from_report
    import argparse

    report_dir = out_dir / "report"
    plan_dir = out_dir / "fix_plan"
    diagnose_inputs(argparse.Namespace(input=str(input_dir), out=str(report_dir), run_id=None))
    plan_from_report(argparse.Namespace(report=str(report_dir), out=str(plan_dir)))


def _write_no_failure_report(out_dir: Path) -> None:
    report_dir = out_dir / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    diagnosis = {
        "schema_version": "failure-doctor-diagnosis/v1",
        "user_facing_category": "证据不足",
        "technical_category": "insufficient_evidence",
        "subtype": "no_failure_signal_found",
        "confidence": 0.2,
        "next_action": "补充 error.log、trace.zip 或 network.json 后重新运行 collect --auto-diagnose",
    }
    _write_json(report_dir / "diagnosis.json", diagnosis)
    (report_dir / "diagnosis.md").write_text(
        "# Agent Failure Diagnosis\n\nNo strong failure signal was found in the collected project folder.\n",
        encoding="utf-8",
    )
    _write_json(report_dir / "evidence.json", {"inputs": {}, "artifact": {}, "diagnosis": diagnosis})
    plan = generate_fix_plan({"failure_type": "insufficient_evidence", "subtype": "no_failure_signal_found", "evidence": []})
    _write_json(report_dir / "fix_plan.json", plan)
    (report_dir / "repair_suggestions.md").write_text("Collect stronger evidence before editing code.\n", encoding="utf-8")
    (report_dir / "codex_fix_prompt.md").write_text("Collect trace.zip, error.log, or network.json before changing code.\n", encoding="utf-8")


def _iter_project_files(project: Path, *, include_hidden: bool) -> Iterable[Path]:
    for path in sorted(project.rglob("*")):
        if path.is_file():
            yield path


def _skip_reason(project: Path, path: Path, *, include_hidden: bool) -> str | None:
    parts = [part.lower() for part in path.relative_to(project).parts]
    if any(part in IGNORED_DIRS for part in parts):
        return "ignored_runtime_or_dependency_dir"
    if any(part in BROWSER_PROFILE_DIRS for part in parts) or path.name.lower() in SENSITIVE_NAMES:
        return "browser_profile_or_credential_store"
    if ".ssh" in parts or path.name.lower() in SENSITIVE_NAMES:
        return "browser_profile_or_credential_store"
    if not include_hidden and any(part.startswith(".") for part in parts):
        return "hidden_file_or_dir"
    return None


def _is_collectable(path: Path) -> bool:
    lower = path.name.lower()
    if lower in {"package.json", "playwright.config.ts", "playwright.config.js", "scrapy.cfg", "pytest.ini"}:
        return True
    return path.suffix.lower() in COLLECTABLE_EXTENSIONS


def _kind_for(path: Path) -> str:
    lower = path.name.lower()
    if lower.endswith(".zip") and "trace" in lower:
        return "trace_zip"
    if lower.endswith((".log", ".txt")):
        return "log"
    if lower.endswith(".json") and "network" in lower:
        return "network"
    if lower.endswith((".png", ".jpg", ".jpeg")):
        return "screenshot_metadata"
    if lower.endswith((".webm", ".mp4")):
        return "recording_metadata"
    return "project_context"


def _detect_failure_signals(project: Path, files: list[dict[str, Any]]) -> list[str]:
    signals: list[str] = []
    for item in files:
        rel = item.get("relative_path")
        if not rel:
            continue
        path = project / str(rel)
        if path.suffix.lower() not in {".log", ".txt", ".json", ".html", ".htm", ".py", ".js", ".ts"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()[:20000]
        for marker in FAILURE_MARKERS:
            if marker in text:
                signals.append(marker.replace(" ", "_"))
    return sorted(set(signals))


def _contains_credentials(redaction_report: dict[str, Any]) -> bool:
    return int(redaction_report.get("total_redactions", 0) or 0) > 0


def _looks_like_broad_scope(project: Path) -> bool:
    if project.parent == project:
        return True
    if project.name.lower().startswith("tmp") and not any(project.iterdir()):
        return True
    broad_names = {"users", "administrator", "documents", "downloads", "desktop"}
    return project.name.lower() in broad_names


def _read_small_texts(project: Path, *, limit: int) -> list[str]:
    texts: list[str] = []
    for path in _iter_project_files(project, include_hidden=False):
        if len(texts) >= limit:
            break
        if _skip_reason(project, path, include_hidden=False) or path.stat().st_size > 200_000:
            continue
        if path.suffix.lower() in {".txt", ".log", ".json", ".py", ".js", ".ts", ".cfg", ".ini", ".toml"} or path.name.lower() == "package.json":
            texts.append(path.read_text(encoding="utf-8", errors="replace")[:5000])
    return texts


def _render_collection_summary(manifest: dict[str, Any]) -> str:
    files = [item for item in manifest["files"] if item.get("included")]
    skipped = manifest.get("skipped_files", [])
    return "\n".join(
        [
            "# Collection Summary",
            "",
            f"- Preset: `{manifest['preset']}`",
            f"- Detected frameworks: `{', '.join(manifest['detected_frameworks'])}`",
            f"- Included files: `{len(files)}`",
            f"- Skipped files: `{len(skipped)}`",
            f"- Failure signals: `{', '.join(manifest['detected_failure_signals'])}`",
            "",
            "Local-only collection finished. Review `open_this_first.md` before sharing anything.",
            "",
        ]
    )


def _render_open_first(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Open This First",
            "",
            "Agent Failure Doctor collected evidence from the project folder you selected.",
            "",
            "## What happened",
            "",
            f"- Project: `{manifest['project_root']}`",
            f"- Output: `{manifest['output_dir']}`",
            f"- Detected frameworks: `{', '.join(manifest['detected_frameworks'])}`",
            f"- Failure signals: `{', '.join(manifest['detected_failure_signals'])}`",
            "",
            "## Safety",
            "",
            "- Local-only: no upload was performed.",
            "- Scope-limited: only the selected project folder was scanned.",
            "- Browser profiles, credential stores, dependency folders, and VCS folders are skipped.",
            "- Share only `sanitized_failure_pack/` after manual review.",
            "",
            "## Next action",
            "",
            "- Read `report/diagnosis.md` when auto diagnosis is enabled.",
            "- Give `ai_handoff/codex_task.md` to Codex only after reviewing the sanitized evidence.",
            "",
        ]
    )


def _snapshot(project: Path, *, ignore: str) -> set[tuple[str, int]]:
    patterns = [item.strip() for item in ignore.split(",") if item.strip()]
    items: set[tuple[str, int]] = set()
    for path in _iter_project_files(project, include_hidden=False):
        rel = path.relative_to(project).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) or rel.startswith(pattern.rstrip("/") + "/") for pattern in patterns):
            continue
        if _skip_reason(project, path, include_hidden=False):
            continue
        items.add((rel, int(path.stat().st_mtime)))
    return items


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_zip(root: Path, zip_path: Path) -> Path:
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path != zip_path:
                archive.write(path, path.relative_to(root).as_posix())
    return zip_path
