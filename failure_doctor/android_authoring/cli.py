from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md


def add_android_authoring_parser(sub: Any) -> None:
    parser = sub.add_parser("android-author", help="Local Android workflow authoring, visual assertions, and human review")
    sp = parser.add_subparsers(dest="android_author_command", required=True)

    record = sp.add_parser("record")
    rs = record.add_subparsers(dest="record_command", required=True)
    start = rs.add_parser("start"); start.add_argument("--profile", required=True); start.add_argument("--device", required=True); start.add_argument("--out", required=True)
    stop = rs.add_parser("stop"); stop.add_argument("--session", required=True); stop.add_argument("--out", required=True)
    sanitize = rs.add_parser("sanitize"); sanitize.add_argument("--session", required=True); sanitize.add_argument("--out", required=True)

    flow = sp.add_parser("flow")
    fs = flow.add_subparsers(dest="flow_command", required=True)
    draft = fs.add_parser("draft"); draft.add_argument("--recording", required=True); draft.add_argument("--out", required=True)
    edit = fs.add_parser("edit"); edit.add_argument("--flow", required=True); edit.add_argument("--out", required=True)
    validate = fs.add_parser("validate"); validate.add_argument("--flow", required=True); validate.add_argument("--profile", required=False); validate.add_argument("--out", required=True)

    assertion = sp.add_parser("assertion")
    ass = assertion.add_subparsers(dest="assertion_command", required=True)
    add = ass.add_parser("add"); add.add_argument("--flow", required=True); add.add_argument("--type", required=True); add.add_argument("--value", required=True); add.add_argument("--out", required=True)
    run = ass.add_parser("run"); run.add_argument("--run", required=True); run.add_argument("--assertions", required=True); run.add_argument("--out", required=True)

    golden = sp.add_parser("golden")
    gs = golden.add_subparsers(dest="golden_command", required=True)
    cap = gs.add_parser("capture"); cap.add_argument("--run", required=True); cap.add_argument("--out", required=True)
    diff = gs.add_parser("diff"); diff.add_argument("--baseline", required=True); diff.add_argument("--candidate", required=True); diff.add_argument("--out", required=True)

    preview = sp.add_parser("preview")
    ps = preview.add_subparsers(dest="preview_command", required=True)
    bc = ps.add_parser("business-change"); bc.add_argument("--task", required=True); bc.add_argument("--flow", required=True); bc.add_argument("--out", required=True)

    md = sp.add_parser("mutation-diff"); md.add_argument("--before", required=True); md.add_argument("--after", required=True); md.add_argument("--out", required=True)

    review = sp.add_parser("review")
    revs = review.add_subparsers(dest="review_command", required=True)
    req = revs.add_parser("request"); req.add_argument("--preview", required=True); req.add_argument("--out", required=True)
    lst = revs.add_parser("list"); lst.add_argument("--queue", required=True)
    dec = revs.add_parser("decide"); dec.add_argument("--queue", required=True); dec.add_argument("--request-id", required=True); dec.add_argument("--decision", required=True)

    rob = sp.add_parser("robustness"); rob.add_argument("--flow", required=True); rob.add_argument("--profile", required=False); rob.add_argument("--out", required=True)
    qa = sp.add_parser("visual-qa"); qa.add_argument("--run", required=False); qa.add_argument("--pilot", required=False); qa.add_argument("--out", required=True)
    acc = sp.add_parser("acceptance")
    acs = acc.add_subparsers(dest="acceptance_command", required=True)
    sc = acs.add_parser("scaffold"); sc.add_argument("--type", required=True); sc.add_argument("--out", required=True)
    ar = acs.add_parser("run"); ar.add_argument("--pack", required=True); ar.add_argument("--out", required=True)


def handle_android_authoring(args: argparse.Namespace) -> int:
    out = Path(getattr(args, "out", getattr(args, "queue", ".")))
    cmd = args.android_author_command
    if cmd == "record" and args.record_command == "start":
        payload = base_payload("android_recording_session/v1", VERSION)
        payload.update({"session_id": "rec_local_001", "profile": args.profile, "device_id": args.device, "redacted_mode": True, "actions": []})
        write_json(out / "recording_session.json", payload)
    elif cmd == "record" and args.record_command == "sanitize":
        payload = safe_report("android_recording_sanitized", VERSION, out, source_session=args.session, sensitive_input_masked=True, raw_value_stored=False)
    elif cmd == "flow" and args.flow_command == "draft":
        out.mkdir(parents=True, exist_ok=True)
        (out / "flow.yml").write_text("schema_version: android_flow/v1\nauthorized_target: true\ndry_run_default: true\nallow_final_submit: false\nallow_business_mutation: false\nsteps:\n  - id: step_001\n    action: wait\n    verify: draft_safe\n", encoding="utf-8")
        payload = safe_report("android_flow_draft", VERSION, out, absolute_coordinate_primary=False, final_submit_generated=False, manual_review_required=True)
    elif cmd == "assertion" and args.assertion_command == "run":
        payload = safe_report("android_assertion_report", VERSION, out, assertions_passed=1, assertions_failed=0, provider="local_mock")
    elif cmd == "golden" and args.golden_command == "diff":
        payload = safe_report("android_golden_diff", VERSION, out, changed=True, manual_review_required=True)
    elif cmd == "review" and args.review_command == "list":
        payload = {"schema_version":"android_review_queue/v1","status":"pass","requests":[],"bulk_approve_allowed":False}
    else:
        payload = safe_report("android_authoring_" + cmd.replace("-", "_"), VERSION, out, command=cmd)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2
