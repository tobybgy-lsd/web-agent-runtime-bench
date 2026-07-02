# Issue Pack Guide

Create:

```powershell
failure-doctor issue-pack create --input .\failed_run --out .\github_issue_pack
failure-doctor issue-pack validate .\github_issue_pack
```

Issue packs contain sanitized summaries for maintainers. They are not raw
failure archives and are safe to attach only after validation passes.
