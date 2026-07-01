# PyPI Release Runbook

Agent Failure Doctor v3.2.5 is ready to publish as the Python package
`agent-failure-doctor`.

Target user install command after publication:

```powershell
pip install agent-failure-doctor
```

## Package Identity

- PyPI package: `agent-failure-doctor`
- CLI: `failure-doctor`
- Compatibility CLI: `trace-doctor`
- Current stable version: `3.2.5`
- Repository: <https://github.com/tobybgy-lsd/web-agent-runtime-bench>

## Local Preflight

Run these from the repository root before uploading:

```powershell
python -m pip install --upgrade build twine
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

Expected result:

- wheel and source distribution are created under `dist/`
- `twine check` reports `PASSED`
- unit tests pass
- local safety scan passes

## Preferred GitHub Path

Use Trusted Publishing from PyPI instead of storing a long-lived token in the
repository.

1. Create the project `agent-failure-doctor` on PyPI.
2. Configure PyPI Trusted Publishing for this GitHub repository.
3. Use the manual GitHub Actions workflow:

```text
.github/workflows/publish-pypi.yml
```

4. Confirm the package page shows version `3.2.5`.
5. Verify a clean install:

```powershell
python -m venv .tmp_pypi_install_check
.\.tmp_pypi_install_check\Scripts\python -m pip install agent-failure-doctor
.\.tmp_pypi_install_check\Scripts\failure-doctor --help
```

## Manual Upload Fallback

Use this only from a private machine with a PyPI API token available in the
current shell:

```powershell
python -m twine upload dist/*
```

Do not commit PyPI tokens, `.pypirc`, shell history, credentials, browser
cookies, or package upload secrets.

## Release Notes Checklist

- GitHub Release exists for the same version.
- `pyproject.toml` version matches the release tag.
- `validation/p98_master_gate.json` reports `overall_status = pass`.
- README points users to the stable CLI and safe evidence-collection flow.
- The first public install command is `pip install agent-failure-doctor`.
