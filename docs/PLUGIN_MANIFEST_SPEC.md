# Plugin Manifest Spec

Every plugin root must contain `plugin_manifest.json` using
`schema_version = failure_doctor_plugin/v1`.

Required fields include:

- `plugin_id`
- `name`
- `version`
- `type`
- `entrypoint`
- `local_only`
- `no_upload`
- `no_external_api`
- `permissions`
- `hooks`
- `safety`

Validation blocks plugins that request network, shell, raw evidence, forbidden
permissions, unknown hooks, missing schemas, private training content, or unsafe
recommendation text.
