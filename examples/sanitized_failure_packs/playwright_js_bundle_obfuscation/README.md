# Playwright JS Bundle Obfuscation

Represents a parser depending on a client bundle whose internal exports or obfuscated symbols changed.

Use it when bundled internals changed and parsing code can no longer find a stable exported parser. The expected diagnosis is `js_bundle_obfuscation`.

