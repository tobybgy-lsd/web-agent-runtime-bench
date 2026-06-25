# Third-Party Reproducibility

This repo is designed so a third party can reproduce the standard benchmark after cloning, with no API keys and no external network during execution.

## Requirements

- Python 3.10+
- Node.js 18+
- PowerShell on Windows, or PowerShell Core where the scripts are available

## Reproduce the Standard Suite

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python tools\benchmark\run_benchmark.py --out-dir sample_run\benchmark --node node
```

Expected result:

- `overall_status`: `PASS`
- `overall_score`: `100.0`
- report files under `sample_run\benchmark`

## CI Equivalent

The GitHub Actions workflow runs:

```powershell
python -m unittest discover -s tests -v
python tools\benchmark\run_benchmark.py --out-dir sample_run\benchmark --node node
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

The workflow uploads the benchmark report as an artifact.

## Reproducibility Boundary

The benchmark is reproducible because it uses local fixtures, synthetic JavaScript bundles, and local mock API verification. It intentionally does not depend on live websites, cookies, accounts, proxies, or private platform behavior.
