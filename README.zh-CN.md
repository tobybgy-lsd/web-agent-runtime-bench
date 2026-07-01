# Agent Failure Doctor 中文文档

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的自动化失败诊断工具，面向 AI Browser Agent、Playwright、爬虫脚本、RPA、截图驱动的 Computer Use 运行，以及文档/表格/表单密集型自动化失败。

- 当前里程碑：Agent Failure Doctor v3.5 OCR & Document Evidence Adapter Pack
- 当前稳定版本：v3.5.0
- 上一个稳定版本：v3.4.0
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
failure-doctor ocr-evidence compare --ocr .\ocr_report --dom .\dom_snapshot.html --out .\ocr_compare
failure-doctor agent-bootstrap --target all --project .
```

## OCR & Document Evidence

v3.5 新增 `failure-doctor ocr-evidence`，用于把截图、PDF、表单、表格、报表、票据、RPA 导出截图、电商 SKU 表、ERP 导出文档中的 OCR/文档结构化结果，转成失败诊断证据。

```powershell
failure-doctor ocr-evidence extract --input .\screenshot.png --out .\ocr_report --provider mock_ocr
failure-doctor ocr-evidence compare --ocr .\ocr_report --dom .\dom_snapshot.html --out .\ocr_compare
failure-doctor ocr-evidence compare-vlm --ocr .\ocr_report --vlm .\vlm_responses.jsonl --out .\ocr_vlm_compare
```

默认 provider 是 mock/local，不默认上传截图、PDF 或文档，不默认调用云 OCR。云 OCR 必须显式授权并经过 safety-evaluate；敏感文档会被 blocked 或要求脱敏。OCR 结果是辅助证据，不是 ground truth。

## Visual Agent Runtime Observability

v3.4 新增 `failure-doctor visual-runtime`，用于分析截图驱动 Agent 的运行链路：

```powershell
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor visual-runtime profile --input .\visual_run --out .\visual_profile
failure-doctor visual-runtime compare --baseline .\run_a --candidate .\run_b --out .\compare_report
failure-doctor visual-runtime adapt --source generic --input .\artifact_dir --out .\visual_run
failure-doctor visual-runtime validate --input .\visual_run --out .\validation_report
```

它会检查截图是否过期、图片压缩和 token 成本、VLM observation 与 action 是否对齐、点击坐标是否漂移、DPR / viewport / scroll 状态是否变化、OCR 文本是否与目标语义冲突，以及可选 DOM 是否与视觉证据冲突。

## 安全边界

这个项目是诊断工具，不是绕过工具。

不提供：

- CAPTCHA 绕过
- 反爬绕过
- 指纹伪造
- 动态签名破解
- 代理池、账号池、IP 池方案
- 人类鼠标轨迹或行为仿真方案
- 真实平台未授权采集流程
- Cookie、Token、浏览器 Profile 或凭据提取

默认行为：

- 本地优先
- 不上传截图、PDF 或文档
- 不默认调用外部 OCR / VLM / LLM
- 不访问真实平台
- 证据不足时输出人工复核或补材料建议

## 常用命令

```powershell
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor verify --before .\before --after .\after --out .\verification
failure-doctor sanitize .\failed_run --out .\shareable_pack
failure-doctor safety-evaluate --project . --out .\safety_report
```

## 验证入口

```powershell
python -m tools.validation.run_ocr_document_evidence_validation
python -m tools.validation.run_visual_agent_runtime_validation
python -m tools.validation.run_p98_master_gate
scripts\local_safety_scan.ps1
scripts\smoke_test.ps1
```

更多文档：

- [OCR Document Evidence Adapter](docs/OCR_DOCUMENT_EVIDENCE_ADAPTER.md)
- [OCR Provider Policy](docs/OCR_PROVIDER_POLICY.md)
- [OCR Safety Boundary](docs/OCR_SAFETY_BOUNDARY.md)
- [Visual Agent Runtime Observability](docs/VISUAL_AGENT_RUNTIME_OBSERVABILITY.md)
- [P98 dashboard](validation/dashboard.md)
