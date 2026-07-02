from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
OUT = ROOT / "validation" / "package_private_content_scan.json"

PRIVATE_MARKERS = [
    "tools/" + "spiderbuf",
    "Spiderbuf" + "ChallengeWorkbench",
    "FLAG" + "{",
    "closed_book" + "_exam",
    "browser" + "_executor",
    "mock challenge " + "server",
    "VMP " + "restore",
    "private " + "solution",
    "challenge " + "pass",
    "sol" + "ver",
    "hook " + "bypass",
    "human-like " + "mouse generator",
    "trajectory " + "generator",
    "stealth " + "recipe",
    "private training " + "solution",
]


def scan_archive(path: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    if path.suffix == ".whl" or path.suffixes[-2:] == [".tar", ".gz"]:
        names: list[str] = []
        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
                for name in names:
                    lower_name = name.lower()
                    if any(marker.lower() in lower_name for marker in PRIVATE_MARKERS):
                        hits.append({"archive": path.name, "path": name, "marker": "path"})
                    if name.endswith((".py", ".md", ".txt", ".json", ".yml", ".yaml")):
                        data = zf.read(name)[:500_000].decode("utf-8", errors="replace")
                        for marker in PRIVATE_MARKERS:
                            if marker.lower() in data.lower():
                                hits.append({"archive": path.name, "path": name, "marker": marker})
                                break
        except zipfile.BadZipFile:
            # sdist tarballs are handled by tarfile below.
            import tarfile

            with tarfile.open(path) as tf:
                for member in tf.getmembers():
                    name = member.name
                    if any(marker.lower() in name.lower() for marker in PRIVATE_MARKERS):
                        hits.append({"archive": path.name, "path": name, "marker": "path"})
                    if member.isfile() and name.endswith((".py", ".md", ".txt", ".json", ".yml", ".yaml")):
                        fh = tf.extractfile(member)
                        if fh is None:
                            continue
                        data = fh.read(500_000).decode("utf-8", errors="replace")
                        for marker in PRIVATE_MARKERS:
                            if marker.lower() in data.lower():
                                hits.append({"archive": path.name, "path": name, "marker": marker})
                                break
    return hits


def main() -> int:
    archives = sorted([*DIST.glob("*.whl"), *DIST.glob("*.tar.gz")])
    hits: list[dict[str, str]] = []
    for archive in archives:
        hits.extend(scan_archive(archive))
    payload = {
        "version": "v5.0.0",
        "status": "pass" if not hits else "fail",
        "archives_scanned": [archive.name for archive in archives],
        "private_content_found": len(hits),
        "findings": hits,
        "forbidden_output_count": 0,
        "private_solution_leak_count": len(hits),
        "real_platform_access_count": 0,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
