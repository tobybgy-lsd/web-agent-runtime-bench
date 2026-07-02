# Agent Failure Doctor 中文文档

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的自动化失败诊断工具，面向 AI
Browser Agent、Playwright、爬虫脚本、RPA、截图驱动的 Computer Use
运行，以及 OCR / 文档 / 表格密集型自动化失败。

- 当前里程碑：Agent Failure Doctor v4.0 Hybrid Evidence Reasoning Pack
- 当前稳定版本：v4.0.0
- 上一稳定版本：v3.9.0 Local Failure Knowledge Base Pack
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
- 证据绑定推理
- causal chain / root-cause graph
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
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --hybrid-reasoning --out .\report
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor agent-bootstrap --target all --project .
```

## v4.0 证据绑定推理

v4.0 新增本地混合推理层：

```powershell
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor root-cause --input .\report --out .\root_cause_report
failure-doctor causal-chain --input .\report --out .\causal_chain_report
failure-doctor ci diagnose --project .\report --out .\ci_report --hybrid-reasoning
```

它会把已脱敏报告转换成 evidence bundle，并生成：

- evidence-bound claims
- competing hypotheses
- causal chain
- root-cause graph
- reasoning validation

确定性诊断仍然是主结论。推理层只能解释和组织证据，不能覆盖高置信度
安全阻断结论。每一条 claim 都必须引用 evidence id；证据不足时必须降级为
`insufficient_evidence`。

## Local Failure Knowledge Base

v3.9 新增本地失败知识库。它只保存脱敏摘要、证据指纹、分类、历史相似案例
和已验证修复建议，默认不上云、不调用外部 embedding API、不保存原始 secret。

```powershell
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report
failure-doctor kb search --kb .\.failure-doctor-kb --query "selector timeout after login redirect"
failure-doctor kb match --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report --out .\kb_match_report
failure-doctor kb export --kb .\.failure-doctor-kb --out .\kb_export --sanitized-only
```

历史修复只作为候选建议，不能跳过本地验证和人工确认直接套用。

## 安全边界

Agent Failure Doctor 不是：

- CAPTCHA 绕过工具
- 反检测工具
- 凭据提取工具
- 未授权采集工具
- 真实平台规避工具

遇到疑似访问限制、权限边界或风控风险时，工具只输出识别、证据、合规分流和
人工复核建议。
