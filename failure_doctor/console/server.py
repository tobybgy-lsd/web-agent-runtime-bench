from __future__ import annotations

import json
import mimetypes
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .readers import build_report_index, read_console_report
from .redaction import dumps_json
from .security import ConsoleSecurityError, assert_host_allowed, safe_join, validate_local_token
from .workspace import append_audit, import_report, init_workspace, list_report_dirs, load_manifest, read_audit
from failure_doctor.kb.store import KnowledgeBase


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
TEMPLATE_DIR = PACKAGE_DIR / "templates"


class ConsoleApp:
    def __init__(
        self,
        *,
        workspace: Path | str,
        host: str = "127.0.0.1",
        port: int = 8765,
        readonly: bool = False,
        allow_lan: bool = False,
        kb: Path | str | None = None,
        enable_hybrid_reasoning: bool = False,
        reasoner: str = "mock_reasoner",
    ) -> None:
        assert_host_allowed(host, allow_lan=allow_lan)
        self.workspace = Path(workspace).expanduser().resolve()
        self.host = host
        self.port = port
        self.readonly = readonly
        self.kb = Path(kb).expanduser().resolve() if kb else None
        self.enable_hybrid_reasoning = enable_hybrid_reasoning
        self.reasoner = reasoner
        self.manifest = init_workspace(self.workspace, host=host, port=port, readonly=readonly)
        self.token = self.manifest["token"]

    def json_response(self, payload: dict[str, Any], status: int = 200) -> tuple[int, dict[str, str], bytes]:
        return (
            status,
            {"Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store"},
            dumps_json(payload).encode("utf-8"),
        )

    def text_response(self, text: str, content_type: str = "text/html; charset=utf-8") -> tuple[int, dict[str, str], bytes]:
        return 200, {"Content-Type": content_type, "Cache-Control": "no-store"}, text.encode("utf-8")

    def error_response(self, message: str, status: int = 400) -> tuple[int, dict[str, str], bytes]:
        return self.json_response({"status": "error", "error": message}, status=status)

    def handle(self, method: str, path: str, headers: dict[str, str], body: bytes) -> tuple[int, dict[str, str], bytes]:
        parsed = urlparse(path)
        route = parsed.path
        try:
            if method == "GET":
                return self._handle_get(route, parsed.query)
            if method == "POST":
                return self._handle_post(route, headers, body)
            return self.error_response("Method not allowed", 405)
        except ConsoleSecurityError as exc:
            return self.error_response(str(exc), 403)
        except Exception as exc:  # pragma: no cover - defensive server boundary
            return self.error_response(f"Console request failed: {exc}", 500)

    def _handle_get(self, route: str, query: str) -> tuple[int, dict[str, str], bytes]:
        if route == "/":
            html = (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")
            return self.text_response(html)
        if route.startswith("/static/"):
            asset = safe_join(STATIC_DIR, route.removeprefix("/static/"))
            content_type = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
            return 200, {"Content-Type": content_type, "Cache-Control": "no-store"}, asset.read_bytes()
        if route == "/api/status":
            return self.json_response(
                {
                    "status": "ok",
                    "version": "v3.7.0",
                    "local_only": True,
                    "host": self.host,
                    "port": self.port,
                    "workspace": str(self.workspace),
                    "readonly": self.readonly,
                    "telemetry": "disabled",
                    "external_assets": "disabled",
                    "knowledge_base": str(self.kb) if self.kb else None,
                    "hybrid_reasoning": {
                        "enabled": self.enable_hybrid_reasoning,
                        "reasoner": self.reasoner,
                        "local_only": True,
                        "raw_content_excluded": True,
                    },
                }
            )
        if route == "/api/reasoning/status":
            return self.json_response(
                {
                    "status": "ok",
                    "enabled": self.enable_hybrid_reasoning,
                    "reasoner": self.reasoner,
                    "local_only": True,
                    "external_api_call_count": 0,
                    "model_download_count": 0,
                    "raw_content_excluded": True,
                }
            )
        if route == "/api/kb/status":
            if not self.kb:
                return self.json_response({"status": "ok", "knowledge_base": None, "enabled": False})
            return self.json_response({"status": "ok", "enabled": True, "health": KnowledgeBase(self.kb).status()})
        if route == "/api/kb/cases":
            if not self.kb:
                return self.json_response({"status": "ok", "cases": []})
            cases = KnowledgeBase(self.kb).list_cases()
            safe_cases = [
                {
                    "case_id": case.get("case_id"),
                    "failure_type": case.get("failure_type"),
                    "subtype": case.get("subtype"),
                    "fix_status": case.get("fix_status"),
                    "safety": case.get("safety"),
                    "evidence_fingerprint": case.get("evidence_fingerprint"),
                }
                for case in cases
            ]
            return self.json_response({"status": "ok", "cases": safe_cases})
        if route == "/api/reports":
            return self.json_response({"status": "ok", "reports": build_report_index(list_report_dirs(self.workspace))})
        if route.startswith("/api/report/"):
            report_id = route.removeprefix("/api/report/").split("/", 1)[0]
            report_dir = safe_join(self.workspace, "reports", report_id)
            payload = read_console_report(report_dir)
            return self.json_response(payload)
        if route == "/api/audit":
            limit = int(parse_qs(query).get("limit", ["100"])[0])
            return self.json_response({"status": "ok", "events": read_audit(self.workspace, limit=limit)})
        if route == "/api/settings":
            manifest = load_manifest(self.workspace)
            return self.json_response(
                {
                    "status": "ok",
                    "settings": {
                        "workspace": manifest.get("workspace"),
                        "local_only": True,
                        "raw_hidden_by_default": True,
                        "post_requires_token": True,
                        "no_external_assets": True,
                    },
                }
            )
        return self.error_response("Not found", 404)

    def _handle_post(self, route: str, headers: dict[str, str], body: bytes) -> tuple[int, dict[str, str], bytes]:
        validate_local_token(headers.get("X-Console-Token"), self.token)
        payload = json.loads(body.decode("utf-8") or "{}")
        if route == "/api/import-report":
            result = import_report(self.workspace, payload.get("path", ""), readonly=self.readonly)
            return self.json_response({"status": "ok", **result})
        if route == "/api/export/share-pack":
            report_id = payload.get("report_id", "")
            report_dir = safe_join(self.workspace, "reports", report_id)
            report = read_console_report(report_dir)
            append_audit(self.workspace, "export_share_pack_preview", {"report_id": report_id})
            return self.json_response(
                {
                    "status": "ok",
                    "shareable": True,
                    "raw_hidden_by_default": True,
                    "report": report,
                }
            )
        if route.startswith("/api/actions/"):
            return self.json_response(
                {
                    "status": "blocked",
                    "reason": "The v3.7 console exposes read-only action previews by default. Run CLI commands explicitly in your terminal.",
                },
                status=409,
            )
        return self.error_response("Not found", 404)


def create_console_app(
    *,
    workspace: Path | str,
    host: str = "127.0.0.1",
    port: int = 8765,
    readonly: bool = False,
    allow_lan: bool = False,
    kb: Path | str | None = None,
    enable_hybrid_reasoning: bool = False,
    reasoner: str = "mock_reasoner",
) -> ConsoleApp:
    return ConsoleApp(
        workspace=workspace,
        host=host,
        port=port,
        readonly=readonly,
        allow_lan=allow_lan,
        kb=kb,
        enable_hybrid_reasoning=enable_hybrid_reasoning,
        reasoner=reasoner,
    )


class _ConsoleRequestHandler(BaseHTTPRequestHandler):
    app: ConsoleApp

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def _dispatch(self, method: str) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        status, headers, payload = self.app.handle(method, self.path, dict(self.headers), body)
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)


def serve_console(app: ConsoleApp, *, open_browser: bool = False) -> int:
    handler = type("ConsoleRequestHandler", (_ConsoleRequestHandler,), {"app": app})
    server = ThreadingHTTPServer((app.host, app.port), handler)
    url = f"http://{app.host}:{app.port}/"
    print(f"Agent Failure Doctor Console: {url}")
    print(f"Workspace: {app.workspace}")
    print(f"Local token for POST actions: {app.token}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Console stopped.")
    finally:
        server.server_close()
    return 0
