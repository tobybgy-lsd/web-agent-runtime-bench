# Agent Failure Doctor 中文文档

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的自动化失败诊断工具，面向 AI Browser Agent、Playwright、爬虫脚本、RPA、截图驱动的 Computer Use 运行，以及 OCR / 文档 / 表格密集型自动化失败。

- 当前里程碑：Agent Failure Doctor v4.1 Enterprise Governance & Role-Based Console Pack
- 当前稳定版本：v4.1.0
- 上一稳定版本：v4.0.0 Hybrid Evidence Reasoning Pack
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

## v4.1 企业治理

v4.1 新增本地企业治理层，用来把诊断、计划、验证、知识库、控制台和 CI 接入同一个安全边界。

```powershell
failure-doctor enterprise init --workspace .\.failure-doctor-enterprise
failure-doctor enterprise user add --workspace .\.failure-doctor-enterprise --id alice --role qa_engineer
failure-doctor enterprise policy list --workspace .\.failure-doctor-enterprise
failure-doctor enterprise request export --workspace .\.failure-doctor-enterprise --user alice --project demo --reason "share sanitized report"
failure-doctor enterprise approve --workspace .\.failure-doctor-enterprise --request-id REQ-0001 --by compliance
failure-doctor enterprise audit export --workspace .\.failure-doctor-enterprise --out .\audit_export
failure-doctor enterprise validate --workspace .\.failure-doctor-enterprise
failure-doctor console --enterprise --workspace .\.failure-doctor-enterprise
failure-doctor ci diagnose --project . --enterprise-workspace .\.failure-doctor-enterprise --out .\ci_report
```

默认策略：

- 只绑定本机地址，默认不开放局域网。
- 不上传原始材料，不启用遥测，不调用外部 API。
- 原始证据访问默认阻断，分享导出默认只允许脱敏材料。
- 敏感操作进入审批流，自动应用补丁不可用。
- 审计日志采用 append-only JSONL，并进行 hash-chain 校验。

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

确定性诊断仍然是主结论。推理层只能解释和组织证据，不能覆盖高置信度安全阻断结论。每一条 claim 都必须引用 evidence id；证据不足时必须降级为 `insufficient_evidence`。

## Local Failure Knowledge Base

v3.9 新增本地失败知识库。它只保存脱敏摘要、证据指纹、分类、历史相似案例和已验证修复建议，默认不上云、不调用外部 embedding API、不保存原始 secret。

```powershell
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report
failure-doctor kb search --kb .\.failure-doctor-kb --query "selector timeout after login redirect"
failure-doctor kb match --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report --out .\kb_match_report
failure-doctor kb export --kb .\.failure-doctor-kb --out .\kb_export --sanitized-only
```

## 安全边界

这个项目不是：

- CAPTCHA 绕过工具
- 反爬规避工具
- 指纹伪造工具
- 账号攻击工具
- 真实平台采集器
- 凭据提取器

它只做本地优先的失败诊断、证据整理、修复计划、验证、脱敏分享和企业治理。
