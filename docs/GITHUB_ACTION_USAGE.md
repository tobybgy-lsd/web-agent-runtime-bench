# GitHub Action Usage

Agent Failure Doctor can run in CI against artifacts already produced by your workflow. It is local-first: the action reads files from the runner workspace and writes a report directory.

```yaml
- name: Diagnose failed automation artifacts
  uses: ./.github/actions/failure-doctor-diagnose
  with:
    input: ./artifacts/failed_run
    out: ./diagnosis_report

- name: Upload diagnosis report
  uses: actions/upload-artifact@v4
  with:
    name: diagnosis-report
    path: ./diagnosis_report
```

You can also call the CLI directly:

```yaml
- name: Diagnose failed automation artifacts
  run: failure-doctor diagnose ./artifacts/failed_run --out ./diagnosis_report
```

For Playwright test-results:

```yaml
- name: Collect Playwright failure pack
  run: failure-doctor collect-playwright ./test-results --out ./failure_pack

- name: Diagnose collected pack
  run: failure-doctor diagnose ./failure_pack --out ./diagnosis_report
```

Do not upload private traces, cookies, tokens, authorization headers, or customer data to public CI logs. Keep sensitive artifacts private and sanitized before sharing.

