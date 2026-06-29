from __future__ import annotations

import argparse
import json

from tools.knowledge_base.load_patterns import load_patterns, pattern_text


def search(query: str) -> list[dict[str, object]]:
    terms = [part.lower() for part in query.replace("/", " ").split() if part.strip()]
    results: list[dict[str, object]] = []
    for pattern in load_patterns():
        haystack = pattern_text(pattern)
        score = sum(1 for term in terms if term in haystack)
        if score:
            results.append(
                {
                    "id": pattern["id"],
                    "score": score,
                    "technical_category": pattern["technical_category"],
                    "subtype": pattern["subtype"],
                    "applies_to": pattern["applies_to"],
                    "path": pattern["_path"],
                }
            )
    return sorted(results, key=lambda item: (-int(item["score"]), str(item["id"])))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    print(json.dumps({"query": args.query, "results": search(args.query)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
