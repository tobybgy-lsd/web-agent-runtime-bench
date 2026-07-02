# Enterprise Approval Workflow

Approval requests cover handoff export, share pack export, raw access, KB export,
patch proposal export, CI gate policy changes, and reasoner provider changes.

```powershell
failure-doctor enterprise request handoff --workspace .\.failure-doctor-enterprise --report .\report --target codex
failure-doctor enterprise approve --workspace .\.failure-doctor-enterprise --request-id req_001 --decision approve
```
