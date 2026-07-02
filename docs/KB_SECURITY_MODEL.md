# KB Security Model

The local failure KB is:

- local-only
- no upload
- no cloud sync
- no external embedding API
- sanitized-only by default
- audit logged

The KB must not store raw secrets, raw customer data, browser profiles,
credential stores, private training solutions, challenge artifacts, or unsafe
automation guidance.

Search and match return redacted summaries and evidence fingerprints only.
