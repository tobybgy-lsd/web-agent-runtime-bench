# Plugin Development Guide

Start with scaffold:

```powershell
failure-doctor plugin scaffold --type framework-adapter --name toy_adapter --out .\plugins\toy_adapter
```

Then edit only local-safe parsing, evidence normalization, or candidate output.
Validate before install:

```powershell
failure-doctor plugin validate .\plugins\toy_adapter
```

Do not include private solvers, real customer data, raw secrets, or unsafe
recommendation logic.
