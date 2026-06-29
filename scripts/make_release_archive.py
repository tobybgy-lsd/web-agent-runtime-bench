from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "AgentFailureDoctor-v0.6.0-source.zip"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a clean git-archive source zip for release review.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="Output zip path")
    parser.add_argument("--ref", default="HEAD", help="Git ref to archive")
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["git", "archive", "--worktree-attributes", "--format=zip", f"--output={out_path}", args.ref],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if completed.returncode != 0:
        print(completed.stdout + completed.stderr)
        return completed.returncode
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
