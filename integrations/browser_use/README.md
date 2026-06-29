# Browser-use / Browser Agent Adapter

This adapter converts local browser-use or browser-agent run logs into an Agent Failure Doctor failure pack.

Supported inputs:

- `agent_history.json`
- browser agent `.log` files
- download failure logs
- CDP disconnect logs
- repeated action loop logs

Python usage:

```python
from integrations.browser_use.adapter import convert_browser_use_run

convert_browser_use_run("agent_history.json", "failure_pack")
```

Then diagnose the pack:

```powershell
failure-doctor diagnose .\failure_pack --out .\report
```

The adapter is local-first and only normalizes user-provided artifacts.

