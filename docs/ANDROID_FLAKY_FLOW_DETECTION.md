# Android Flaky Flow Detection

The flaky detector scans local run artifacts for repeated device, Android version,
locator, permission, network, and WebView dimensions.

```powershell
failure-doctor android-ops flaky detect --runs .\ops_run --out .\flaky_report
```

Safe next actions focus on evidence comparison, stable locators, and manual review.
It does not recommend unauthorized network, account, or platform workarounds.

