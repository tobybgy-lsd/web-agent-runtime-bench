# Android Business Data Binding

Business data binding maps CSV, JSON, JSONL, SQLite, and optionally XLSX rows into
local Android Ops tasks. Secret-like fields such as password, token, cookie, secret,
authorization, and auth headers are rejected.

```powershell
failure-doctor android-ops data bind --flow .\flows\post_image_text.yml --data .\tasks.csv --out .\bound_tasks
```

Price, SKU, inventory, publishing, and transaction changes remain dry-run by default
and must pass mutation guard checks.

