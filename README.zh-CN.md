# Agent Failure Doctor 中文文档

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的自动化失败诊断工具，面向 AI Browser Agent、Playwright、爬虫脚本、RPA、截图驱动的 Computer Use 运行，以及 OCR / 文档 / 表格密集型自动化失败。

- 当前里程碑：Agent Failure Doctor v3.9 Local Failure Knowledge Base Pack
- 当前稳定版本：v3.9.0
- 上一个稳定版本：v3.8.0
- P98 controlled maturity gate：已通过

## 输入

支持本地脱敏材料：

- `trace.zip`
- `error.log`
- `console.txt`
- `network.json`
- `probe_report.json`
- screenshot metadata
- `visual_run/`
- OCR / document evidence
- `user_description.txt`

## 输出

- 失败诊断
- 证据链
- 下一步行动
- 修复建议
- GitHub issue 草稿
- Codex / Claude / Cursor 修复提示
- 可分享的脱敏报告包

## 快速开始

```powershell
python -m pip install agent-failure-doctor
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench

failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize
failure-doctor ocr-evidence extract --input .\screenshot.png --out .\ocr_report --provider mock_ocr
failure-doctor regulated-eval --suite all --out .\regulated_report
failure-doctor full-chain-eval --input .\failed_run --out .\full_chain_report
failure-doctor console --import-report .\full_chain_report --open
failure-doctor ci run --input .\full_chain_report --out .\ci_report --fail-on high
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\full_chain_report
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --out .\report
failure-doctor agent-bootstrap --target all --project .
```

## Local Failure Knowledge Base

v3.9 新增本地失败知识库。它只保存脱敏摘要、证据指纹、分类、历史相似案例和已验证修复建议，默认不上传、不云同步、不调用外部 embedding API。

```powershell
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report
failure-doctor kb search --kb .\.failure-doctor-kb --query "selector timeout after login redirect"
failure-doctor kb match --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report --out .\kb_match_report
failure-doctor kb export --kb .\.failure-doctor-kb --out .\kb_export --sanitized-only
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --out .\report
```

历史修复只作为候选建议，不能跳过本地验证和人工确认直接套用。

## CI/CD Integration

v3.8 新增本地 CI gate 与模板：

```powershell
failure-doctor ci run --input .\report --out .\ci_report --fail-on high
failure-doctor ci validate --input .\ci_report --out .\ci_validation
failure-doctor ci templates --out .\ci_templates
```

## Local Web Console

v3.7 新增本地报告控制台：

```powershell
failure-doctor console
failure-doctor console --host 127.0.0.1 --port 8765 --workspace .\.failure-doctor-console
failure-doctor console --import-report .\report --open
```

默认只绑定 `127.0.0.1`，不上传、不遥测、不加载外部 CDN。POST 操作需要本地 token，原始本地证据默认隐藏。

## 安全边界

Agent Failure Doctor 不是 CAPTCHA 绕过工具，不是反风控规避工具，不是账号攻击工具，不是真实平台采集器，不会发布私有训练材料或本地解题细节。公开版本只保留诊断、证据、合规修复建议、验证和脱敏分享能力。
