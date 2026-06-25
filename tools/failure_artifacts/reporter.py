"""Markdown and HTML rendering for failure artifact diagnoses."""

from __future__ import annotations

import html
from typing import Any, Mapping

from .report import render_markdown_report as _render_markdown_report


def render_markdown_report(diagnosis: Mapping[str, Any], artifact: Mapping[str, Any]) -> str:
    return _render_markdown_report(artifact, diagnosis)


def render_html_report(diagnosis: Mapping[str, Any], artifact: Mapping[str, Any]) -> str:
    evidence = "\n".join(f"<li>{html.escape(str(item))}</li>" for item in diagnosis.get("evidence", []))
    fixes = "\n".join(f"<li>{html.escape(str(item))}</li>" for item in diagnosis.get("suggested_fix", []))
    title = html.escape(str(diagnosis.get("failure_type", "unknown")))
    run_id = html.escape(str(artifact.get("run_id", "unknown")))
    tool = html.escape(str(artifact.get("tool", "unknown")))
    confidence = html.escape(f"{float(diagnosis.get('confidence', 0)):.0%}")
    summary = html.escape(str(artifact.get("summary", "")))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Failure Diagnosis - {title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 880px; margin: 40px auto; line-height: 1.55; }}
    code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 4px; }}
    .meta {{ color: #555; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #eee; }}
  </style>
</head>
<body>
  <h1>Failure Diagnosis Report</h1>
  <p class="meta">Run <code>{run_id}</code> · Tool <code>{tool}</code></p>
  <p><span class="badge">{title}</span> confidence <strong>{confidence}</strong></p>
  <h2>Summary</h2>
  <p>{summary}</p>
  <h2>Evidence</h2>
  <ul>{evidence or "<li>No evidence generated.</li>"}</ul>
  <h2>Suggested Fix</h2>
  <ul>{fixes or "<li>Manual review required.</li>"}</ul>
  <h2>Safety</h2>
  <p>No cookies, tokens, passwords, or Authorization headers should be included in submitted artifacts.</p>
</body>
</html>
"""
