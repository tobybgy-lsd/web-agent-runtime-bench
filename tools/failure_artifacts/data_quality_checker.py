# -*- coding: utf-8 -*-
"""
数据工程稳定性检测模块
Data Engineering Stability Checker

涵盖:
- Schema 字段验证 (schema validation)
- 去重键检测 (dedupe key)
- 断点续跑支持 (checkpoint)
- 重试/退避策略检测 (retry/backoff)
- 死信队列 (dead letter queue)
- 运行清单 (run manifest)
- 数据来源哈希 (source hash)
- 字段质量报告 (field quality report)
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

# 延迟导入，避免循环依赖（仅在参数启用时才会实际使用）
try:
    from .bloom_deduper import BloomDedupeChecker
except ImportError:
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from bloom_deduper import BloomDedupeChecker
    except ImportError:
        BloomDedupeChecker = None  # type: ignore

try:
    from .structured_logger import StructuredLogger, TraceContext, create_logger
except ImportError:
    try:
        from structured_logger import StructuredLogger, TraceContext, create_logger
    except ImportError:
        StructuredLogger = None  # type: ignore
        TraceContext = None      # type: ignore
        create_logger = None     # type: ignore


# ─────────────────────────── Schema Validation ───────────────────────────

class SchemaValidator:
    """Validates each scraped record against an expected schema definition."""

    def __init__(self, schema: dict[str, type]):
        """
        schema: e.g. {"title": str, "price": float, "url": str, "in_stock": bool}
        """
        self.schema = schema

    def validate(self, record: dict) -> dict:
        """Returns a validation result dict with ok/errors/warnings."""
        errors = []
        warnings = []
        for field, expected_type in self.schema.items():
            if field not in record:
                errors.append(f"MISSING field: '{field}'")
            elif record[field] is None:
                warnings.append(f"NULL value for field: '{field}'")
            elif not isinstance(record[field], expected_type):
                actual = type(record[field]).__name__
                errors.append(f"TYPE_MISMATCH field: '{field}' expected {expected_type.__name__} got {actual}")
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# ─────────────────────────── Dedupe Key ───────────────────────────

class DedupeChecker:
    """Detects duplicate records by a composite dedupe key."""

    def __init__(self, key_fields: list[str]):
        self.key_fields = key_fields
        self._seen: set[str] = set()
        self.duplicate_count = 0
        self.total_seen = 0

    def compute_key(self, record: dict) -> str:
        parts = [str(record.get(f, "")) for f in self.key_fields]
        return "|".join(parts)

    def is_duplicate(self, record: dict) -> bool:
        key = self.compute_key(record)
        self.total_seen += 1
        if key in self._seen:
            self.duplicate_count += 1
            return True
        self._seen.add(key)
        return False

    def report(self) -> dict:
        return {
            "unique_seen": len(self._seen),
            "duplicates_found": self.duplicate_count
        }


# ─────────────────────────── Checkpoint ───────────────────────────

class CheckpointManager:
    """Saves and loads scraping progress so runs can resume after failure."""

    def __init__(self, checkpoint_file: str | Path):
        self.path = Path(checkpoint_file)
        self._state: dict = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                self._state = json.load(f)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2)

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value
        self.save()

    def mark_page_done(self, page: int) -> None:
        done = self._state.get("done_pages", [])
        if page not in done:
            done.append(page)
            self._state["done_pages"] = done
            self.save()

    def is_page_done(self, page: int) -> bool:
        return page in self._state.get("done_pages", [])

    def summary(self) -> dict:
        return {
            "checkpoint_file": str(self.path),
            "done_pages": self._state.get("done_pages", []),
            "last_cursor": self._state.get("cursor"),
            "total_saved": self._state.get("total_saved", 0)
        }


# ─────────────────────────── Retry / Backoff ───────────────────────────

class RetryPolicy:
    """Configures exponential backoff retry strategy with jitter."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._attempt = 0
        self._total_retries = 0

    def reset(self) -> None:
        self._attempt = 0

    def next_delay(self) -> float:
        """Returns the next backoff delay in seconds (exponential + jitter)."""
        import random
        delay = min(self.base_delay * (2 ** self._attempt), self.max_delay)
        jitter = random.uniform(0, delay * 0.2)
        self._attempt += 1
        self._total_retries += 1
        return delay + jitter

    def can_retry(self) -> bool:
        return self._attempt < self.max_retries

    def report(self) -> dict:
        return {
            "max_retries": self.max_retries,
            "current_attempt": self._attempt,
            "total_retries_across_session": self._total_retries
        }


# ─────────────────────────── Dead Letter Queue ───────────────────────────

class DeadLetterQueue:
    """Stores failed records/URLs that exceeded max retries for later review."""

    def __init__(self, dlq_file: str | Path):
        self.path = Path(dlq_file)
        self._entries: list[dict] = []

    def push(self, url: str, error: str, data: dict | None = None) -> None:
        self._entries.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "url": url,
            "error": error,
            "data": data or {}
        })

    def flush(self) -> int:
        """Writes DLQ entries to disk and returns count flushed."""
        if not self._entries:
            return 0
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, indent=2, ensure_ascii=False)
        count = len(self._entries)
        self._entries.clear()
        return count

    def report(self) -> dict:
        return {
            "dlq_file": str(self.path),
            "pending_entries": len(self._entries)
        }


# ─────────────────────────── Run Manifest ───────────────────────────

class RunManifest:
    """Records metadata about a scraping run for audit and replay."""

    def __init__(self, manifest_file: str | Path):
        self.path = Path(manifest_file)
        self._data: dict = {
            "run_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "end_time": None,
            "status": "running",
            "pages_scraped": 0,
            "records_total": 0,
            "records_valid": 0,
            "records_duplicate": 0,
            "records_failed": 0,
            "source_hash": None,
        }

    def update(self, **kwargs) -> None:
        self._data.update(kwargs)

    def finish(self, status: str = "success") -> None:
        self._data["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._data["status"] = status
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def get_run_id(self) -> str:
        return self._data["run_id"]

    def report(self) -> dict:
        return dict(self._data)


# ─────────────────────────── Source Hash ───────────────────────────

def compute_source_hash(html_or_content: str) -> str:
    """SHA-256 hash of the raw source page content for change detection."""
    return hashlib.sha256(html_or_content.encode("utf-8", errors="replace")).hexdigest()


def compare_source_hashes(current_hash: str, previous_hash: str) -> dict:
    """Detects if the source page has changed since last scrape."""
    changed = current_hash != previous_hash
    return {
        "source_changed": changed,
        "current_hash": current_hash,
        "previous_hash": previous_hash,
        "alert": "source changed - validate selectors and extraction assumptions" if changed else "source unchanged"
    }


# ─────────────────────────── Field Quality Report ───────────────────────────

class FieldQualityReporter:
    """Generates per-field quality statistics across a batch of records."""

    def __init__(self, schema_fields: list[str]):
        self.schema_fields = schema_fields
        self._total = 0
        self._field_stats: dict[str, dict] = {
            f: {"present": 0, "null": 0, "empty": 0, "type_ok": 0, "type_errors": 0}
            for f in schema_fields
        }

    def ingest(self, record: dict, schema: dict[str, type] | None = None) -> None:
        self._total += 1
        for field in self.schema_fields:
            val = record.get(field, "__MISSING__")
            stat = self._field_stats[field]
            if val == "__MISSING__":
                continue
            stat["present"] += 1
            if val is None:
                stat["null"] += 1
            elif val == "" or val == [] or val == {}:
                stat["empty"] += 1
            if schema and field in schema:
                if isinstance(val, schema[field]):
                    stat["type_ok"] += 1
                else:
                    stat["type_errors"] += 1

    def report(self) -> dict:
        total = max(self._total, 1)
        result = {}
        for field, stat in self._field_stats.items():
            fill_rate = stat["present"] / total
            result[field] = {
                "fill_rate": f"{fill_rate:.1%}",
                "null_count": stat["null"],
                "empty_count": stat["empty"],
                "type_errors": stat["type_errors"],
                "quality": "good" if fill_rate >= 0.95 else ("warn" if fill_rate >= 0.80 else "poor")
            }
        return {
            "total_records": self._total,
            "fields": result
        }


# ─────────────────────────── All-in-one Pipeline ───────────────────────────

class DataEngineeringPipeline:
    """
    Combines all data engineering stability tools into a single pipeline.

    可选扩展:
      - use_bloom=True: 用 BloomDedupeChecker 替代 DedupeChecker（内存更友好）
      - enable_structured_log=True: 启用结构化 JSONL 日志，记录每条 record 处理结果
    """

    def __init__(
        self,
        schema: dict[str, type],
        dedupe_keys: list[str],
        output_dir: str | Path,
        use_bloom: bool = False,
        enable_structured_log: bool = False,
        bloom_capacity: int = 1_000_000,
        bloom_fpr: float = 0.001,
    ):
        """
        初始化 DataEngineeringPipeline。

        Args:
            schema: 字段 schema 定义，如 {"title": str, "price": float}
            dedupe_keys: 用于去重的字段列表
            output_dir: 输出目录（checkpoint、manifest、DLQ 等均写入此目录）
            use_bloom: 是否使用 BloomFilter 去重（默认 False，使用原 set-based DedupeChecker）
            enable_structured_log: 是否启用结构化 JSONL 日志（默认 False）
            bloom_capacity: BloomFilter 容量（use_bloom=True 时有效），默认 100 万
            bloom_fpr: BloomFilter 目标误报率（use_bloom=True 时有效），默认 0.001
        """
        out = Path(output_dir)
        self.schema_validator = SchemaValidator(schema)
        self.output_dir = out
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # ── 去重器选择 ──
        self.use_bloom = use_bloom
        if use_bloom:
            if BloomDedupeChecker is None:
                raise ImportError(
                    "use_bloom=True 需要 bloom_deduper.py 可被导入，"
                    "请确认该文件位于同一目录或 sys.path 中。"
                )
            self.deduper = BloomDedupeChecker(
                key_fields=dedupe_keys,
                capacity=bloom_capacity,
                fpr=bloom_fpr,
            )
        else:
            self.deduper = DedupeChecker(dedupe_keys)

        self.checkpoint = CheckpointManager(out / "checkpoint.json")
        self.retry = RetryPolicy(max_retries=3, base_delay=1.0)
        self.dlq = DeadLetterQueue(out / "dead_letter_queue.json")
        self.manifest = RunManifest(out / "run_manifest.json")
        self.quality = FieldQualityReporter(list(schema.keys()))

        # ── 结构化日志 ──
        self.enable_structured_log = enable_structured_log
        self._logger: Any = None  # StructuredLogger 实例（可选）
        if enable_structured_log:
            if create_logger is None:
                raise ImportError(
                    "enable_structured_log=True 需要 structured_logger.py 可被导入，"
                    "请确认该文件位于同一目录或 sys.path 中。"
                )
            run_id = self.manifest.get_run_id()
            self._logger = create_logger(out / "logs", run_id=run_id)
            self._logger.info(
                "DataEngineeringPipeline 初始化完成",
                None,
                use_bloom=use_bloom,
                bloom_capacity=bloom_capacity if use_bloom else None,
                bloom_fpr=bloom_fpr if use_bloom else None,
            )

        # 记录 record 处理序号（用于生成 TraceContext）
        self._record_idx = 0

    def _make_ctx(self, page_num: int | None = None, record_idx: int | None = None, url: str | None = None):
        """创建当前 pipeline 运行的 TraceContext（仅在启用结构化日志时使用）。"""
        if TraceContext is None:
            return None
        return TraceContext(
            run_id=self.manifest.get_run_id(),
            session_id=self.manifest.get_run_id(),
            page_num=page_num,
            record_idx=record_idx,
            url=url,
        )

    def process_record(self, record: dict, page_num: int | None = None, url: str | None = None) -> dict:
        """
        验证、去重并追踪单条记录，返回处理结果。

        Args:
            record: 要处理的数据记录
            page_num: 当前页码（可选，用于结构化日志）
            url: 当前 URL（可选，用于结构化日志）

        Returns:
            dict 包含: status、record、issues
        """
        self._record_idx += 1
        result = {"status": "ok", "record": record, "issues": []}

        # 1. Schema validation
        validation = self.schema_validator.validate(record)
        if not validation["ok"]:
            result["issues"].extend(validation["errors"])
            result["status"] = "schema_error"

        # 2. Dedupe check
        if self.deduper.is_duplicate(record):
            result["status"] = "duplicate"
            result["issues"].append("DUPLICATE record detected via dedupe key")

        # 3. Field quality ingestion
        self.quality.ingest(record, self.schema_validator.schema)

        # 4. Manifest update
        self.manifest.update(records_total=self.deduper.total_seen)

        # 5. 结构化日志记录
        if self._logger is not None:
            ctx = self._make_ctx(
                page_num=page_num,
                record_idx=self._record_idx,
                url=url,
            )
            self._logger.log_record(
                ctx=ctx,
                record=record,
                status=result["status"],
                issues=result["issues"],
            )

        return result

    def final_report(self) -> dict:
        """Returns a comprehensive summary of the pipeline run."""
        self.manifest.finish("success")
        report = {
            "manifest": self.manifest.report(),
            "deduplication": self.deduper.report(),
            "checkpoint": self.checkpoint.summary(),
            "retry": self.retry.report(),
            "dead_letter_queue": self.dlq.report(),
            "field_quality": self.quality.report(),
        }

        # 如果启用了结构化日志，将日志摘要加入报告
        if self._logger is not None:
            log_summary = self._logger.summary()
            report["log_summary"] = log_summary
            self._logger.info("pipeline final_report 生成完毕", None, report_keys=list(report.keys()))

        return report

    def save_final_report(self) -> Path:
        """将最终报告写入 data_quality_report.json 并返回路径。"""
        report = self.final_report()
        report_path = self.output_dir / "data_quality_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        # 关闭日志文件
        if self._logger is not None:
            self._logger.close()
        return report_path
