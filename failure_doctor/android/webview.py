from __future__ import annotations


def expected_contexts(package_name: str) -> list[str]:
    return ["NATIVE_APP", f"WEBVIEW_{package_name}"]
