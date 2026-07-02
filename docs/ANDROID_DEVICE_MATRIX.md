# Android Device Matrix

The Android Pro device matrix runner is a mock/local validation surface for checking workflow metadata across device descriptors.

```powershell
failure-doctor android-pro matrix run --matrix .\matrix.yml --flow .\flow.yml --out .\matrix_report
```

It does not connect to real devices unless future authorized adapters explicitly provide evidence.
