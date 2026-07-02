from __future__ import annotations


def normalize_text_input(text: str) -> str:
    return text.replace("\r\n", "\n")
