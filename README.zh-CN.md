# Agent Failure Doctor

[English documentation](README.md)

![CI](https://github.com/tobybgy-lsd/web-agent-runtime-bench/actions/workflows/benchmark.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Agent Failure Doctor 是一个**本地优先**的自动化失败诊断工具，面向
AI Browser Agent、Playwright、RPA、爬虫自动化和数据采集脚本调试。

- 当前里程碑：Agent Failure Doctor v3.2 Auto Collector P98 Gate
- 上一个 P98 稳定线：Agent Failure Doctor v3.1.0 P98 Master Gate
- 上一个 P95 稳定线：Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack

**输入：** `trace.zip` / `error.log` / `console.txt` / `network.json` /
截图 metadata / `user_description.txt`

**输出：** 诊断结论、证据、下一步、修复建议、GitHub issue 草稿、
Codex 修复 Prompt、脱敏报告包。

## 快速开始

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m pip install -e .

failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize
failure-doctor agent-bootstrap --target all --project .
```

## 分发与真实反馈

v3.2.0 是当前稳定技术基线。下一阶段重点是分发和真实用户反馈，
不是继续堆 synthetic 功能。

- PyPI 发布手册：[docs/PYPI_RELEASE.md](docs/PYPI_RELEASE.md)
- 2 分钟演示脚本：[docs/DEMO_VIDEO_SCRIPT.md](docs/DEMO_VIDEO_SCRIPT.md)
- 技术文章草稿：[docs/TECH_ARTICLE_DRAFT.md](docs/TECH_ARTICLE_DRAFT.md)
- 真实用户反馈闭环：[docs/REAL_USER_FEEDBACK_LOOP.md](docs/REAL_USER_FEEDBACK_LOOP.md)

PyPI 发布后的目标安装命令：

```powershell
pip install agent-failure-doctor
```

## 一键本地采集与诊断

```powershell
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize

failure-doctor watch --project . --out .\failure_reports --once --auto-diagnose
failure-doctor run --capture -- python .\examples\mock_script_fails.py
```

非技术 Windows 用户可以双击
`scripts/windows/Start-FailureDoctor-Diagnosis.bat`，也可以把失败项目文件夹
拖到这个 BAT 上。

`collect` 只扫描你授权的项目文件夹，不扫描整台电脑，不读取浏览器用户资料、
凭据库、SSH key、`.git`、`node_modules` 或虚拟环境目录，也不会上传任何文件。
对外分享前只应查看并分享 `sanitized_failure_pack/`。

## AI 前端调用

Agent Failure Doctor 可以作为不同 AI coding agent 的本地诊断后端：

```powershell
failure-doctor agent-bootstrap --target all --project .
```

它会生成：

```text
.failure-doctor/
├── AGENT_ENTRYPOINT.md
└── agents/<target>/
    ├── instructions.md
    ├── diagnose_project.md
    ├── repair_workflow.md
    ├── allowed_commands.md
    └── forbidden_actions.md
```

支持的前端包括：

`codex` / `cursor` / `claude_code` / `vscode_copilot` / `antigravity` /
`opencode` / `qoder` / `trae` / `workbuddy` / `openclaw` / `hermes` /
`generic_agent`

## 生命周期

```text
collect / run / adapt
  -> diagnose
  -> plan
  -> handoff / propose-patch
  -> verify
  -> sanitize / share
```

常用命令：

```powershell
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor handoff .\report --target codex --out .\ai_handoff
failure-doctor propose-patch --repo . --report .\report --out .\patch_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification
failure-doctor sanitize .\failure_doctor_auto_report --out .\shareable_failure_pack
failure-doctor batch .\runs --out .\batch_report
```

## 报告内容

```text
report/
├── diagnosis.json
├── diagnosis.md
├── evidence.json
├── input_summary.json
├── issue_draft.md
├── repair_suggestions.md
├── codex_fix_prompt.md
└── failure_doctor_report.zip
```

报告会说明：

- 最可能的失败类别和技术子类
- 支撑判断的证据
- 缺少哪些材料
- 修复建议和验证命令
- 可以交给 Codex / Claude Code / Cursor 的修复 Prompt

## 当前验证

- P98 master gate：通过
- Auto Collector validation：95 个本地 fixture case，通过
- 安全扫描：0 forbidden output
- GitHub Actions：Windows / Ubuntu / macOS 均运行单测和验证

查看：

- [Validation Dashboard](validation/dashboard.md)
- [P98 Limits](docs/P98_LIMITS.md)
- [Agent Frontend Invocation](docs/AGENT_FRONTEND_INVOCATION.md)
- [Safety Boundary](docs/safety_boundary.md)

## 安全边界

本项目只做本地、授权、脱敏材料的失败诊断。

它不是：

- CAPTCHA 处理工具
- 风控规避工具
- 指纹伪造工具
- 凭据提取工具
- 未授权采集工具
- 真实平台采集框架

如果诊断结果显示疑似访问限制或合规风险，工具只会给出安全分流建议：
确认授权、降低请求量、使用官方 API、联系平台、改成人工审核流程或停止自动化。

## 贡献失败案例

你不需要写代码。最有价值的贡献是提交一个脱敏失败案例。

欢迎提交脱敏后的：

- `error.log`
- `trace.zip`
- `console.txt`
- `network.json`
- screenshot metadata
- `user_description.txt`

不要提交密码、cookie、token、authorization header、API key、私有 URL、
个人数据、客户数据或任何敏感信息。

如果你允许，适合公开的案例会进入 validation corpus。模板和作者自己生成的
示例不计入外部验证指标。
