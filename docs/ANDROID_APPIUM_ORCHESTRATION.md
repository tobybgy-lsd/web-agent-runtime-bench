# Android Appium Orchestration

The Android Ops Appium layer creates local session plans for devices in a farm.
It does not install Appium, download drivers, start remote Appium servers, or call
external services.

```powershell
failure-doctor android-ops appium plan --farm .\android_farm --out .\appium_plan
failure-doctor android-ops appium start-session --device mock-emulator-5554 --port 4723 --out .\session_report
```

Session reports are planning artifacts for local operators and CI smoke tests.

