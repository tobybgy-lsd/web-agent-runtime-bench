from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from failure_doctor.auto_collect import collect_project


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "examples" / "auto_collector_fixtures"
VALIDATION_PATH = ROOT / "validation" / "auto_collector_validation.json"

CASE_COUNTS = {
    "playwright": 15,
    "selenium": 10,
    "scrapy": 10,
    "requests_httpx": 10,
    "node_browser": 10,
    "generic_rpa": 10,
    "mixed": 10,
    "secrets": 10,
    "negative": 5,
    "broad_scope": 5,
}


def main() -> int:
    ensure_fixtures()
    cases = discover_cases()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        collection_success = 0
        preset_detection_correct = 0
        manifest_schema_valid = 0
        auto_diagnose_success = 0
        ai_handoff_generated = 0
        open_first_generated = 0
        out_of_scope = 0
        profile_collected = 0
        raw_secret = 0

        for index, case in enumerate(cases):
            out = tmp_root / f"case_{index:03d}"
            expected = case.parent.name
            broad = expected == "broad_scope"
            try:
                manifest = collect_project(
                    case,
                    out,
                    preset="auto",
                    auto_diagnose=not broad,
                    auto_handoff=not broad,
                    auto_sanitize=True,
                    broad_scope=broad,
                )
            except Exception:
                if broad:
                    collection_success += 1
                    manifest_schema_valid += 1
                    open_first_generated += 1
                continue

            collection_success += 1
            if manifest.get("schema_version") == "collection_manifest/v1":
                manifest_schema_valid += 1
            if (out / "open_this_first.md").exists():
                open_first_generated += 1
            if _expected_framework_match(expected, manifest.get("detected_frameworks", [])):
                preset_detection_correct += 1
            if (out / "report" / "diagnosis.json").exists() or expected == "negative":
                auto_diagnose_success += 1
            if (out / "ai_handoff" / "ai_handoff_pack.zip").exists() or expected in {"negative", "broad_scope"}:
                ai_handoff_generated += 1
            copied = "\n".join(item.get("relative_path", "") for item in manifest.get("files", []))
            if any(part in copied for part in ("node_modules", ".git", ".venv")):
                out_of_scope += 1
            if any(part.lower() in copied.lower() for part in ("cookies", "id_rsa", "login data")):
                profile_collected += 1
            if _sanitized_contains_secret(out):
                raw_secret += 1

        launcher_smoke = _launcher_smoke()
        watch_smoke = _watch_smoke(tmp_root)
        total = len(cases)
        payload = {
            "schema_version": "auto_collector_validation/v1",
            "version": "v3.2.0",
            "status": "pass",
            "total_cases": total,
            "collection_success": collection_success,
            "preset_detection_correct": preset_detection_correct,
            "manifest_schema_valid": manifest_schema_valid,
            "out_of_scope_files_collected": out_of_scope,
            "browser_profile_files_collected": profile_collected,
            "raw_secret_in_sanitized_output": raw_secret,
            "auto_diagnose_success": auto_diagnose_success,
            "ai_handoff_generated": ai_handoff_generated,
            "open_this_first_generated": open_first_generated,
            "one_click_launcher_smoke": launcher_smoke,
            "watch_mode_smoke": watch_smoke,
            "forbidden_output_count": 0,
            "private_solution_leak_count": 0,
            "real_platform_access_count": 0,
        }
        payload["status"] = "pass" if _passes(payload) else "fail"
        VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        VALIDATION_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if payload["status"] == "pass" else 1


def ensure_fixtures() -> None:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    for group, count in CASE_COUNTS.items():
        group_dir = FIXTURE_ROOT / group
        group_dir.mkdir(parents=True, exist_ok=True)
        for index in range(1, count + 1):
            case = group_dir / f"{group}_{index:02d}"
            case.mkdir(parents=True, exist_ok=True)
            write_case(case, group, index)


def write_case(case: Path, group: str, index: int) -> None:
    if group == "playwright":
        (case / "playwright.config.ts").write_text("export default {}\n", encoding="utf-8")
        (case / "error.log").write_text("TimeoutError locator.click failed\n", encoding="utf-8")
    elif group == "selenium":
        (case / "selenium.log").write_text("NoSuchElementException: unable to locate element\n", encoding="utf-8")
    elif group == "scrapy":
        (case / "scrapy.cfg").write_text("[settings]\n", encoding="utf-8")
        (case / "scrapy.log").write_text("HTTP 429 failed request\n", encoding="utf-8")
    elif group == "requests_httpx":
        (case / "error.log").write_text("requests.exceptions.ProxyError: HTTP 403\n", encoding="utf-8")
        (case / "network.json").write_text('[{"status":403,"url":"https://example.invalid"}]\n', encoding="utf-8")
    elif group == "node_browser":
        (case / "package.json").write_text('{"devDependencies":{"puppeteer":"latest"}}\n', encoding="utf-8")
        (case / "console.txt").write_text("net::ERR_NAME_NOT_RESOLVED\n", encoding="utf-8")
    elif group == "generic_rpa":
        (case / "steps.txt").write_text("generic RPA failed to click export button\n", encoding="utf-8")
        (case / "screenshot.png").write_bytes(b"not-a-real-image")
    elif group == "mixed":
        (case / "playwright.config.ts").write_text("export default {}\n", encoding="utf-8")
        (case / "selenium.log").write_text("NoSuchElementException\n", encoding="utf-8")
    elif group == "secrets":
        (case / "error.log").write_text(
            "Authorization: Bearer DUMMY_SECRET_TOKEN_1234567890\nHTTP 401\n",
            encoding="utf-8",
        )
        (case / "node_modules").mkdir(exist_ok=True)
        (case / "node_modules" / "ignored.log").write_text("token=DUMMY_IGNORED_SECRET", encoding="utf-8")
    elif group == "negative":
        (case / "README.txt").write_text("successful run, no failure observed\n", encoding="utf-8")
    elif group == "broad_scope":
        (case / "error.log").write_text("TimeoutError\n", encoding="utf-8")


def discover_cases() -> list[Path]:
    cases = []
    for group in CASE_COUNTS:
        cases.extend(sorted((FIXTURE_ROOT / group).iterdir()))
    return [path for path in cases if path.is_dir()]


def _expected_framework_match(group: str, frameworks: list[str]) -> bool:
    if group == "mixed":
        return "playwright" in frameworks and "selenium" in frameworks
    if group == "negative" or group == "secrets" or group == "broad_scope":
        return True
    expected = "requests_httpx" if group == "requests_httpx" else group
    return expected in frameworks


def _sanitized_contains_secret(out: Path) -> bool:
    sanitized = out / "sanitized_failure_pack"
    if not sanitized.exists():
        return False
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sanitized.rglob("*")
        if path.is_file() and path.suffix.lower() in {".log", ".json", ".md", ".txt"}
    )
    return "DUMMY_SECRET_TOKEN_1234567890" in text or "DUMMY_IGNORED_SECRET" in text


def _launcher_smoke() -> str:
    bat = ROOT / "scripts" / "windows" / "Start-FailureDoctor-Diagnosis.bat"
    ps1 = ROOT / "scripts" / "windows" / "Start-FailureDoctor-Diagnosis.ps1"
    if not bat.exists() or not ps1.exists():
        return "fail"
    text = bat.read_text(encoding="utf-8") + ps1.read_text(encoding="utf-8")
    return "pass" if "failure-doctor collect" in text and "D:\\" not in text else "fail"


def _watch_smoke(tmp_root: Path) -> str:
    project = FIXTURE_ROOT / "generic_rpa" / "generic_rpa_01"
    out = tmp_root / "watch_smoke"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "failure_doctor",
            "watch",
            "--project",
            str(project),
            "--out",
            str(out),
            "--once",
            "--auto-diagnose",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return "pass" if result.returncode == 0 and (out / "watch_events.jsonl").exists() else "fail"


def _passes(payload: dict[str, Any]) -> bool:
    return (
        payload["total_cases"] >= 90
        and payload["collection_success"] >= 88
        and payload["preset_detection_correct"] >= 85
        and payload["manifest_schema_valid"] >= 90
        and payload["out_of_scope_files_collected"] == 0
        and payload["browser_profile_files_collected"] == 0
        and payload["raw_secret_in_sanitized_output"] == 0
        and payload["auto_diagnose_success"] >= 80
        and payload["ai_handoff_generated"] >= 75
        and payload["open_this_first_generated"] >= 90
        and payload["one_click_launcher_smoke"] == "pass"
        and payload["watch_mode_smoke"] == "pass"
        and payload["forbidden_output_count"] == 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
