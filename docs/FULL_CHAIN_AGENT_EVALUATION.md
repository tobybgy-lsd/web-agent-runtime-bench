# Full-Chain Agent Evaluation

`failure-doctor full-chain-eval` summarizes the local failure lifecycle:

```text
collect -> diagnose -> plan -> handoff -> patch proposal -> verify
-> sanitize/share -> safety-evaluate -> OCR evidence -> visual-runtime
-> regulated-eval
```

Run:

```powershell
failure-doctor full-chain-eval --input .\failed_run --out .\full_chain_report --include-safety --include-ocr --include-visual --include-regulated
```

Outputs:

- `full_chain_evaluation.json`
- `full_chain_evaluation.md`
- `stage_results.json`

The report highlights missing stages, blocking failures, unsafe AI handoff, and
unsafe share-pack conditions. It does not execute patches and does not contact
external APIs.

If unsafe handoff or unsafe sharing is blocked, sanitize the local artifact pack
before pasting anything into an AI frontend.
