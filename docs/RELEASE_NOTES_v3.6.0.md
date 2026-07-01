# Agent Failure Doctor v3.6.0 - Regulated Industry & Pure Visual Agent Full-Chain Evaluation Pack

v3.6.0 adds local-only regulated industry workflow evaluation and full-chain
agent evaluation on top of the existing OCR/document evidence, visual runtime,
safety, and P98 gate layers.

## What changed

- Added `failure-doctor regulated-eval` for synthetic finance, government,
  healthcare, and cross-industry mock workflow evaluation.
- Added `failure-doctor full-chain-eval` to summarize collect, diagnose, plan,
  handoff, patch proposal, verify, sanitize/share, safety, OCR, visual runtime,
  and regulated evaluation signals.
- Raised the visual runtime validation gate to v3.6 thresholds with 160+ local
  cases, pure visual no-DOM support, and zero external VLM calls or screenshot
  uploads.
- Added P98 pillars for `regulated_industry_workflow_pack`,
  `visual_agent_runtime_observability`, and `full_chain_agent_evaluation`.
- Added agent-bootstrap workflows for regulated and full-chain evaluation.

## Safety

- Regulated suites are synthetic/mock only.
- The tool does not access real finance, government, healthcare, patient,
  citizen, bank, or customer systems.
- No screenshot, PDF, document, VLM, OCR, or report upload happens by default.
- No private Spiderbuf, solver, FLAG, challenge, hook, VMP, or private training
  solution content is included in the public package.
- Forbidden outputs remain blocked: no CAPTCHA bypass, anti-bot evasion,
  fingerprint spoofing, signature cracking, proxy/account/IP-pool guidance,
  protected challenge automation, credential extraction, or browser profile
  reading.

## Known limits

- Regulated workflow evaluation is not legal, medical, financial, or regulatory
  compliance advice.
- Full-chain evaluation scores local artifact completeness and safety gates; it
  does not automatically prove that a source-code patch is correct.
- Visual runtime diagnosis uses offline artifacts and local/mock evidence by
  default; external providers require explicit user-side policy choices outside
  the default workflow.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.6.0
failure-doctor --help
failure-doctor regulated-eval --suite all --out .\regulated_report
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor full-chain-eval --input .\failed_run --out .\full_chain_report --include-safety --include-ocr --include-visual --include-regulated

python -m tools.validation.run_regulated_industry_validation
python -m tools.validation.run_visual_agent_runtime_validation
python -m tools.validation.run_full_chain_agent_evaluation
python -m tools.validation.run_p98_master_gate
```

PyPI: [https://pypi.org/project/agent-failure-doctor/](https://pypi.org/project/agent-failure-doctor/)

Forbidden output count: 0.
