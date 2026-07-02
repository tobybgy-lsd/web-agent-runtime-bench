from __future__ import annotations


def allocate_ports(index: int, base_appium: int = 4723, base_system: int = 8201) -> dict[str, int]:
    return {"appium_port": base_appium + index, "system_port": base_system + index}

