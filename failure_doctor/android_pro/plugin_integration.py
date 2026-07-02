from __future__ import annotations


def android_pro_plugin_hooks() -> list[str]:
    return ["android_pro.profile", "android_pro.flow_lint", "android_pro.locator_heal"]
