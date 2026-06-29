# Manual GitHub Release Update for v3.2.0

Use this only if `gh release edit v3.2.0 --notes-file docs/RELEASE_NOTES_v3.2.0.md` cannot run.

1. Open the release:
   [https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.2.0](https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.2.0)
2. Click **Edit**.
3. Add this Quick Install block near the top of the release body:

   ```powershell
   python -m pip install agent-failure-doctor
   failure-doctor --help
   ```

4. Add the PyPI link:
   [https://pypi.org/project/agent-failure-doctor/](https://pypi.org/project/agent-failure-doctor/)
5. Click **Update release**.
