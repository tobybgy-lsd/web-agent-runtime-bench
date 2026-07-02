# Android Locator Registry

The locator registry ranks stable Android locators such as resource id, accessibility description, text, and class hierarchy.

```powershell
failure-doctor android-pro locator-registry build --ui-dump .\ui.xml --out .\registry
failure-doctor android-pro locator-registry validate --registry .\registry\android_locator_registry.json
```

Coordinate-primary locators are blocked.
