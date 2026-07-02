# Android Mutation Guard

Mutation Guard blocks publishing, submitting, payment, ordering, price changes, SKU
changes, inventory changes, and similar production state changes by default.

```powershell
failure-doctor android-ops mutation-check --flow .\flows\edit_sku_price.yml --out .\mutation_guard
```

Save-draft, dry-run, and screenshot verification flows are allowed when they are
authorized and public-safe.
