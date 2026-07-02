# Plugin SDK

Agent Failure Doctor plugins extend local evidence collection, normalization,
candidate diagnosis, reporting, console views, CI summaries, KB patterns,
reasoning tools, and validation packs.

Plugins are local-only by default and disabled by default.

```powershell
failure-doctor plugin scaffold --type framework-adapter --name toy_adapter --out .\plugins\toy_adapter
failure-doctor plugin validate .\plugins\toy_adapter
failure-doctor plugin install .\plugins\toy_adapter --workspace .\.failure-doctor-plugins
failure-doctor plugin enable toy_adapter --workspace .\.failure-doctor-plugins
```

Core rules:

- manifest required
- permissions required
- no upload by default
- no network by default
- no shell by default
- no raw evidence by default
- enterprise governance applies
- safety gate applies
- plugin outputs are candidates, not final truth

See also:

- [Plugin Manifest Spec](PLUGIN_MANIFEST_SPEC.md)
- [Plugin Permission Model](PLUGIN_PERMISSION_MODEL.md)
- [Plugin Security Sandbox](PLUGIN_SECURITY_SANDBOX.md)
- [Plugin Hook API](PLUGIN_HOOK_API.md)
- [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- [Plugin Validation Guide](PLUGIN_VALIDATION_GUIDE.md)
