from __future__ import annotations

from pathlib import Path

from .server import create_console_app, serve_console
from .workspace import import_report


def run_console(args) -> int:
    app = create_console_app(
        workspace=Path(args.workspace),
        host=args.host,
        port=args.port,
        readonly=args.readonly,
        allow_lan=args.allow_lan,
        kb=getattr(args, "kb", None),
        enable_hybrid_reasoning=bool(getattr(args, "enable_hybrid_reasoning", False)),
        reasoner=str(getattr(args, "reasoner", "mock_reasoner")),
    )
    if args.import_report:
        import_report(app.workspace, args.import_report, readonly=args.readonly)
    if args.import_batch:
        import_report(app.workspace, args.import_batch, readonly=args.readonly)
    open_browser = bool(args.open and not getattr(args, "no_browser", False))
    return serve_console(app, open_browser=open_browser)
