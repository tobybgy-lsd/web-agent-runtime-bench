"""Android APK UI automation evidence adapter.

The Android adapter is local-first and safety-bound. It normalizes Appium,
ADB/uiautomator, logcat, screenshot, and flow evidence into the same
diagnose/plan/verify workflow without attempting account, captcha, device,
or platform risk bypasses.
"""

ANDROID_SCHEMA_VERSION = "android_apk_adapter/v1"
ANDROID_ADAPTER_VERSION = "6.0.0"

__all__ = ["ANDROID_SCHEMA_VERSION", "ANDROID_ADAPTER_VERSION"]
