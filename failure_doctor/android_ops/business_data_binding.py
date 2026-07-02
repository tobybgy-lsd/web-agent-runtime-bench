from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any

from .ops_audit import write_json
from .safety import scan_forbidden_text

SECRET_FIELDS = {"password", "token", "cookie", "secret", "authorization", "auth_header"}


def bind_data(flow: Path, data: Path, out: Path) -> dict[str, Any]:
    rows = _load_rows(data)
    blocked = []
    tasks = []
    for idx, row in enumerate(rows, start=1):
        lower_keys = {str(key).lower() for key in row}
        forbidden = scan_forbidden_text(row)
        if SECRET_FIELDS & lower_keys or forbidden:
            blocked.append({"row": idx, "reason": "secret_or_forbidden_data", "forbidden": forbidden})
            continue
        task_id = row.get("task_id") or f"task_{idx:03d}"
        tasks.append(
            {
                "task_id": task_id,
                "flow": str(flow),
                "mode": row.get("mode", "dry_run"),
                "data": _sanitize_row(row),
                "allow_business_mutation": False,
            }
        )
    payload = {
        "schema_version": "android_business_data_binding/v1",
        "status": "pass" if not blocked else "blocked",
        "flow": str(flow),
        "task_count": len(tasks),
        "blocked_count": len(blocked),
        "tasks": tasks,
        "blocked_rows": blocked,
        "local_only": True,
        "no_upload": True,
    }
    write_json(out / "bound_tasks.json", payload)
    _write_jsonl(out / "tasks.jsonl", tasks)
    return payload


def _load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else payload.get("tasks", [])
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if suffix in {".sqlite", ".db"}:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            table = conn.execute("select name from sqlite_master where type='table' order by name limit 1").fetchone()
            if not table:
                return []
            return [dict(row) for row in conn.execute(f"select * from {table['name']}")]
    if suffix == ".xlsx":
        try:
            import openpyxl  # type: ignore
        except Exception:
            return []
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [str(cell) for cell in rows[0]]
        return [dict(zip(headers, row)) for row in rows[1:]]
    return []


def _sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if str(key).lower() not in SECRET_FIELDS}


def _write_jsonl(path: Path, tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(task, ensure_ascii=False) for task in tasks) + ("\n" if tasks else ""), encoding="utf-8")

