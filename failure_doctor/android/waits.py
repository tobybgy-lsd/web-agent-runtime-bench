from __future__ import annotations


def bounded_wait_seconds(value: float, *, minimum: float = 0.1, maximum: float = 30.0) -> float:
    return max(minimum, min(maximum, float(value)))
