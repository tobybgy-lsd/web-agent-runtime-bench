# Android UI Tree Diff

UI tree diff compares two UIAutomator XML dumps and reports likely locator drift, text drift, content description drift, class changes, and bounds changes.

```powershell
failure-doctor android-pro ui-diff --old .\old.xml --new .\new.xml --out .\diff
```
