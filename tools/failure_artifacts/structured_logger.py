# -*- coding: utf-8 -*-
"""
结构化日志链路模块
Structured Logger with trace_id chain

特性:
- JSONL 格式输出 (每条日志一行 JSON)
- trace_id 贯穿爬虫全链路: run_id → page → record → field
- 支持 info / warn / error 分级
- 专用方法: log_record / log_page / log_field_quality
- 运行汇总统计
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────────────────
# TraceContext — 链路追踪上下文
# ─────────────────────────────────────────────────────────────────────────

class TraceContext:
    """
    单次操作的追踪上下文，贯穿 run → page → record → field 层级。
    
    用法:
        run_ctx  = TraceContext(run_id="run_abc123")
        page_ctx = run_ctx.with_page(1, url="https://shop.com/products?page=1")
        rec_ctx  = page_ctx.with_record(5, url="https://shop.com/p/42")
    """

    def __init__(
        self,
        run_id: str | None = None,
        session_id: str | None = None,
        page_num: int | None = None,
        record_idx: int | None = None,
        url: str | None = None,
    ):
        # 自动生成 run_id (若未指定)
        if run_id is None:
            run_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.run_id = run_id
        self.session_id = session_id or run_id
        self.page_num = page_num
        self.record_idx = record_idx
        self.url = url

    def with_page(self, page_num: int, url: str | None = None) -> "TraceContext":
        """派生出页面层级上下文。"""
        return TraceContext(
            run_id=self.run_id,
            session_id=self.session_id,
            page_num=page_num,
            record_idx=None,
            url=url or self.url,
        )

    def with_record(self, record_idx: int, url: str | None = None) -> "TraceContext":
        """派生出记录层级上下文。"""
        return TraceContext(
            run_id=self.run_id,
            session_id=self.session_id,
            page_num=self.page_num,
            record_idx=record_idx,
            url=url or self.url,
        )


    def derive(
        self,
        run_id: str | None = None,
        session_id: str | None = None,
        page_num: int | None = None,
        record_idx: int | None = None,
        url: str | None = None,
    ) -> "TraceContext":
        """从当前上下文派生，并覆盖指定属性。"""
        return TraceContext(
            run_id=run_id if run_id is not None else self.run_id,
            session_id=session_id if session_id is not None else self.session_id,
            page_num=page_num if page_num is not None else self.page_num,
            record_idx=record_idx if record_idx is not None else self.record_idx,
            url=url if url is not None else self.url,
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"run_id": self.run_id, "session_id": self.session_id}
        if self.page_num is not None:
            d["page_num"] = self.page_num
        if self.record_idx is not None:
            d["record_idx"] = self.record_idx
        if self.url:
            d["url"] = self.url
        return d


# ─────────────────────────────────────────────────────────────────────────
# StructuredLogger
# ─────────────────────────────────────────────────────────────────────────

class StructuredLogger:
    """
    结构化 JSONL 日志记录器，trace_id 贯穿全链路。

    每条日志格式:
    {
        "ts": "2026-07-01T12:00:00Z",
        "level": "INFO",
        "trace_id": "run_abc123#0042",
        "run_id": "run_abc123",
        "msg": "page scraped",
        "page_num": 2,
        "count": 20,
        "elapsed_ms": 312.5
    }
    """

    def __init__(
        self,
        log_file: str | Path,
        run_id: str | None = None,
        also_print: bool = False,
    ):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id or hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.also_print = also_print
        self._seq = 0
        self._stats = {
            "total": 0, "info": 0, "warn": 0, "error": 0,
            "pages_logged": 0, "records_logged": 0,
        }
        self._fh = open(self.log_file, "a", encoding="utf-8")

    def _write(self, level: str, msg: str, ctx: TraceContext | None, **extra: Any) -> None:
        self._seq += 1
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "trace_id": f"{self.run_id}#{self._seq:04d}",
            "run_id": self.run_id,
            "msg": msg,
        }
        if ctx:
            entry.update(ctx.to_dict())
        if extra:
            entry.update(extra)

        line = json.dumps(entry, ensure_ascii=False)
        self._fh.write(line + "\n")
        self._fh.flush()

        self._stats["total"] += 1
        self._stats[level.lower()] = self._stats.get(level.lower(), 0) + 1

        if self.also_print:
            lvl_color = {"INFO": "", "WARN": "WARN ", "ERROR": "ERROR "}.get(level, "")
            ctx_str = f" [page={ctx.page_num}]" if ctx and ctx.page_num else ""
            print(f"  [{level}]{ctx_str} {lvl_color}{msg}", file=sys.stderr)

    def info(self, msg: str, ctx: TraceContext | None = None, **extra: Any) -> None:
        self._write("INFO", msg, ctx, **extra)

    def warn(self, msg: str, ctx: TraceContext | None = None, **extra: Any) -> None:
        self._write("WARN", msg, ctx, **extra)

    def error(self, msg: str, ctx: TraceContext | None = None, **extra: Any) -> None:
        self._write("ERROR", msg, ctx, **extra)

    def log_record(
        self,
        ctx: TraceContext,
        record: dict,
        status: str,
        issues: list[str],
    ) -> None:
        """专用: 记录单条数据记录的处理结果。"""
        level = "INFO" if status == "ok" else ("WARN" if status == "duplicate" else "ERROR")
        self._write(
            level,
            f"record processed: {status}",
            ctx,
            record_id=record.get("id"),
            record_title=str(record.get("title", ""))[:40],
            status=status,
            issues=issues,
            issues_count=len(issues),
        )
        self._stats["records_logged"] += 1

    def log_page(
        self,
        ctx: TraceContext,
        page_num: int,
        count: int,
        elapsed_ms: float,
    ) -> None:
        """专用: 记录页面爬取完成。"""
        self._write(
            "INFO",
            f"page {page_num} scraped: {count} records in {elapsed_ms:.0f}ms",
            ctx,
            page_num=page_num,
            record_count=count,
            elapsed_ms=round(elapsed_ms, 2),
        )
        self._stats["pages_logged"] += 1

    def log_field_quality(self, ctx: TraceContext, report: dict) -> None:
        """专用: 记录字段质量报告。"""
        fields_summary = {
            f: v.get("quality", "?")
            for f, v in report.get("fields", {}).items()
        }
        self._write(
            "INFO",
            "field quality report",
            ctx,
            total_records=report.get("total_records", 0),
            fields=fields_summary,
        )

    def summary(self) -> dict[str, Any]:
        """返回日志统计汇总。"""
        return {
            "log_file": str(self.log_file),
            "run_id": self.run_id,
            "total_log_entries": self._stats["total"],
            "errors": self._stats.get("error", 0),
            "warnings": self._stats.get("warn", 0),
            "infos": self._stats.get("info", 0),
            "pages_logged": self._stats["pages_logged"],
            "records_logged": self._stats["records_logged"],
        }

    def close(self) -> None:
        """关闭日志文件句柄。"""
        if self._fh and not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> "StructuredLogger":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


# ─────────────────────────────────────────────────────────────────────────
# 工厂函数
# ─────────────────────────────────────────────────────────────────────────

def create_logger(
    output_dir: str | Path,
    run_id: str | None = None,
    also_print: bool = False,
) -> StructuredLogger:
    """
    工厂函数: 在 output_dir 下创建 structured_run.jsonl 日志文件。
    
    Args:
        output_dir: 输出目录 (自动创建)
        run_id: 可选的稳定 run 标识符
        also_print: 是否同时打印到 stderr
    
    Returns:
        StructuredLogger 实例
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "structured_run.jsonl"
    return StructuredLogger(log_path, run_id=run_id, also_print=also_print)
