# Android Locator Self-Healing

Locator self-healing is recommendation-only.

```powershell
failure-doctor android-pro locator-heal --old-ui .\old.xml --new-ui .\new.xml --failed-locator com.example:id/save --out .\heal
```

The report includes candidate locators, similarity signals, and manual approval requirements. It does not auto-apply changes.
