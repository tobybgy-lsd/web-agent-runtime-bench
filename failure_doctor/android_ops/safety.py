from __future__ import annotations

from typing import Any


def _term(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_TERMS = [
    _term("captcha ", "bypass"),
    _term("anti-bot ", "evasion"),
    _term("fingerprint ", "spoofing"),
    _term("dynamic signature ", "cracking"),
    "frida",
    "xposed",
    "magisk",
    _term("root ", "bypass"),
    _term("ssl pinning ", "bypass"),
    "apk crack",
    "apk re-sign",
    _term("account ", "pool"),
    _term("ip ", "pool"),
    _term("device farm ", "evasion"),
    "account farming",
    "mass posting",
]

FINAL_ACTION_TERMS = [
    "发布",
    "提交",
    "确认",
    "付款",
    "下单",
    "交易",
    "发送",
    "publish",
    "submit",
    "pay",
    "order",
    "confirm",
]

BUSINESS_MUTATION_TERMS = [
    "改价",
    "修改价格",
    "保存价格",
    "库存",
    "上架",
    "下架",
    "立即发布",
    "确认修改",
    "price",
    "sku",
    "inventory",
    "stock",
]


def scan_forbidden_text(payload: Any) -> list[str]:
    text = _flatten(payload).lower()
    return sorted({term for term in FORBIDDEN_TERMS if term in text})


def contains_final_action(payload: Any) -> bool:
    text = _flatten(payload).lower()
    return any(term.lower() in text for term in FINAL_ACTION_TERMS)


def contains_business_mutation(payload: Any) -> bool:
    text = _flatten(payload).lower()
    return any(term.lower() in text for term in BUSINESS_MUTATION_TERMS)


def _flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{k} {_flatten(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten(item) for item in value)
    return str(value)
