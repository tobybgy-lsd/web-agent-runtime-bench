# Plugin Hook API

Supported hook names include:

- `collect.adapter`
- `diagnose.rule_candidate`
- `evidence.normalize`
- `console.page`
- `ci.summary_section`
- `kb.fingerprint`
- `reasoning.tool`
- `report.exporter`
- `validation.case_provider`

Hook output must include the plugin id and must be schema-valid. Hook output is
an extension result; the core pipeline decides whether to use it.
