# Agent Failure Doctor

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的 AI 自动化失败诊断工具，面向 AI Browser Agent、Playwright、RPA、爬虫自动化和数据采集脚本调试。

输入：
`trace.zip` / `error.log` / `console.txt` / `network.json` / 截图 metadata / `user_description.txt`

输出：
诊断结论、证据、下一步、修复建议、GitHub issue 草稿、Codex 修复 Prompt。

## 快速开始

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m pip install -e .
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

## 输出文件

```text
report/
|-- diagnosis.json
|-- diagnosis.md
|-- evidence.json
|-- input_summary.json
|-- issue_draft.md
|-- repair_suggestions.md
|-- codex_fix_prompt.md
`-- failure_doctor_report.zip
```

## 验证修复是否真的成功

```powershell
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification_report
```

`verify` 会对比 before/after 证据，判断原失败是否已解决、是否未解决、是否变成另一个失败，或证据不足。

## v0.9 验证状态

- 131 条 source ledger 记录，并区分真实公开 issue、官方文档行为边界、public-inspired sanitized 记录
- 50 条可追溯真实公开 issue 记录
- 30 个由 Playwright 原生生成的 `trace.zip` fixtures
- 真实 trace 验证：30/30 合理分类
- 真实 trace 验证：30/30 精确 subtype
- 62 条 external public reference seed
- 20 条 external public reference held-out 记录
- external public reference 验证：20/20 合理分类，20/20 可执行下一步
- 12 组 resolution validation before/after 案例
- resolution validation：12/12 状态判断正确
- external held-out 验证：10 条公开来源记录，9/10 合理分类，10/10 可执行下一步
- 生成报告和 Prompt 的 forbidden output 为 0

详见 [validation/dashboard.md](validation/dashboard.md)、[docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md) 和 [docs/EXTERNAL_DATA_SOURCES.md](docs/EXTERNAL_DATA_SOURCES.md)。

## 复现真实 Trace 验证

```powershell
python -m pip install -e .[trace-gen]
python -m tools.real_trace_generation.generate_real_trace_fixtures --out .\examples\realistic_playwright_traces --count 30 --clean
python -m tools.validation.run_real_trace_validation
python -m tools.validation.run_external_public_reference_validation
python -m tools.validation.run_resolution_validation
python scripts\validate_external_heldout.py
```

## 安全边界

本项目只做本地、脱敏材料诊断，不上传 trace、日志、cookie、token、网络包或截图。

本项目不是：

- 挑战页面自动处理工具
- 访问控制规避工具
- 凭据提取工具
- 真实平台采集器
- 未授权采集工具

如果疑似遇到平台访问限制或风控边界，工具只给出识别、分流和合规建议，例如使用官方 API、确认授权、降低访问量、联系平台或停止未授权采集。

## 贡献失败案例

你不需要写代码。最有价值的贡献是提交一个脱敏失败案例。

请提供：

- 使用的工具：Playwright / browser-use / Scrapy / requests / Codex / RPA / other
- 输入类型：trace.zip / error.log / console.txt / network.json / screenshot / description
- 失败现象
- 预期行为
- 实际行为
- 脱敏错误摘要
- 是否可以变成公开测试案例

不要提交密码、cookie、token、authorization header、API key、私有 URL、private data、个人数据或客户数据。

欢迎提交脱敏后的 `error.log`、`trace.zip`、`console.txt`、`network.json`、截图 metadata 或 `user_description.txt`。如果你允许，案例会获得 `EXT-YYYY-NNNN` 编号，并在不先调规则的情况下用当前发布版本 first-run 一次，结果进入 [外部验证仪表盘](validation/external_validation_dashboard.md)。

模板和作者自己生成的示例不计入外部验证指标。详细流程见 [docs/external_validation_protocol.md](docs/external_validation_protocol.md) 和 [docs/REAL_TRACE_CONTRIBUTION_GUIDE.md](docs/REAL_TRACE_CONTRIBUTION_GUIDE.md)。

## Applied Scenario Demos

Local-only mock demos show how Agent Failure Doctor diagnoses failures in hot product collection, live commerce monitoring, ecommerce listing automation, authorized content publishing workflow, GUI/RPA data bridge, and ERP-to-ecommerce sync.

```powershell
python -m tools.validation.run_applied_scenario_validation
```

These demos are failure diagnosis packs, not production business systems.

Current result: 18/18 reasonable classifications, 18/18 valid fix plans, 18/18 correct verification statuses, 0 forbidden outputs.
