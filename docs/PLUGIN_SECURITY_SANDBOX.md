# Plugin Security Sandbox

The v4.2 sandbox is a policy sandbox:

- input/output path guard
- path traversal guard
- symlink guard
- sensitive path guard
- permission guard
- validation guard
- audit guard
- fail-closed behavior

Plugins cannot load remote assets, upload raw evidence, execute shell commands,
or access browser profiles by default.
