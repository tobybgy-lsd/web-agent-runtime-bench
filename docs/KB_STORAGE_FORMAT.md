# KB Storage Format

Default storage is plain files:

```text
.failure-doctor-kb/
├── kb_manifest.json
├── audit_log.jsonl
├── cases/
│   └── case_000001/
│       ├── case.json
│       ├── diagnosis_summary.md
│       ├── evidence_fingerprint.json
│       ├── fix_summary.md
│       ├── verification_summary.json
│       └── safety_metadata.json
├── indexes/
├── fixes/
└── exports/
```

The format is local-first and database-free by default. Indexes can be rebuilt
with:

```powershell
failure-doctor kb rebuild-index --kb .\.failure-doctor-kb
```
