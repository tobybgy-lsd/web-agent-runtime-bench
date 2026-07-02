# Plugin Validation Guide

Run:

```powershell
failure-doctor plugin validate .\plugins\toy_adapter
python -m tools.validation.run_plugin_sdk_ecosystem_validation
python -m tools.validation.run_p98_master_gate
```

Validation checks manifest schema, permissions, hooks, entrypoint, schemas,
safety metadata, forbidden terms, private training markers, and high-risk access
defaults.
