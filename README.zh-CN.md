# Agent Failure Doctor 中文文档

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的自动化失败诊断工具，面向 AI Browser Agent、Playwright、爬虫脚本、RPA、截图驱动的 Computer Use 运行，以及 OCR / 文档 / 表格密集型自动化失败。

- 当前里程碑：Agent Failure Doctor v5.1 Android APK UI Automation Adapter Pack
- 当前稳定版本：v5.1.0
- 上一稳定版本：v5.0.1 README stable baseline wording patch
- 上一稳定版本：v5.0.0 Stable API / Schema / Plugin ABI Standardization Release
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
failure-doctor agent-bootstrap --target all --project .
```

## v5.1 Android APK UI Automation Adapter

```powershell
failure-doctor android doctor --out .\android_doctor
failure-doctor android validate-flow .\examples\android_apk_cases\post_image_text_dry_run\input\flow.yml --out .\android_flow
failure-doctor android dump-ui .\examples\android_apk_cases\ui_tree_basic\input\ui.xml --out .\android_ui
failure-doctor diagnose .\examples\android_apk_cases\permission_dialog_blocked\input --adapter android-apk --out .\android_diag
failure-doctor collect --adapter android-apk --input .\examples\android_apk_cases\permission_dialog_blocked\input --out .\android_pack
```

v5.1 新增本地优先的 Android APK UI 自动化证据适配层，用于授权 / mock app 的 Appium 日志、ADB/uiautomator XML、logcat 摘要、截图元数据和 flow 文件诊断。默认 dry-run，不自动做最终提交；最终提交必须显式审批。公开项目只做诊断、证据归一化、合规建议和安全拦截，不发布本地私有训练解法。

## v4.3 Real User Case Program & Public Benchmark

```powershell
failure-doctor case intake --input .\raw_failure_pack --out .\sanitized_case
failure-doctor case publish-check --case .\sanitized_case
failure-doctor issue-pack create --input .\raw_failure_pack --out .\issue_pack
failure-doctor benchmark run --suite public-safe --out .\benchmark_public
failure-doctor benchmark compare --baseline .\benchmark_public --candidate .\benchmark_public --out .\benchmark_compare
```

v4.3 鎶婄湡瀹炵敤鎴峰け璐ユ潗鏂欐敹闆嗗拰鍏叡 benchmark 鍙樻垚 public-safe 流程：先脱敏，再校验，再生成 issue pack 或 benchmark report。默认本地运行，不上传，不调用外部 API，不发布私有训练解法。

## v5.0 Stable API / Schema / Plugin ABI

```powershell
failure-doctor adapter api diagnose --input .\newman_report.json --out .\api_report
failure-doctor deploy health --workspace .\.failure-doctor-enterprise --out .\health_report
failure-doctor stability check-api --out .\stability_report
```

v5.0 锁定稳定 CLI、schema registry、plugin ABI、benchmark case format、public case manifest 和 enterprise policy baseline。默认本地优先、不上传、不调用外部 API、不发布本地私有训练解法。
## v4.2 Plugin SDK

```powershell
failure-doctor plugin scaffold --type framework-adapter --name toy_adapter --out .\plugins\toy_adapter
failure-doctor plugin validate .\plugins\toy_adapter
failure-doctor plugin install .\plugins\toy_adapter --workspace .\.failure-doctor-plugins
failure-doctor plugin enable toy_adapter --workspace .\.failure-doctor-plugins
failure-doctor plugin run toy_adapter --workspace .\.failure-doctor-plugins --input .\sample_artifacts --out .\plugin_report
```

Plugin SDK 用于在安全边界内扩展：

- framework adapter
- evidence adapter
- diagnosis rule
- industry pack
- Console extension
- CI extension
- KB pattern
- reasoning tool
- report exporter
- validation pack

插件安全边界：

- 默认 disabled
- 必须有 `plugin_manifest.json`
- 必须声明 permissions
- 默认 local-only
- 默认 no upload
- 默认 no network
- 默认 no shell
- 默认 no raw evidence access
- 插件输出只能作为 candidate
- core validator、safety gate、enterprise policy、RBAC、approval、audit 始终生效

## v4.1 企业治理

```powershell
failure-doctor enterprise init --workspace .\.failure-doctor-enterprise
failure-doctor enterprise user add --workspace .\.failure-doctor-enterprise --username alice --role developer
failure-doctor console --enterprise --workspace .\.failure-doctor-enterprise --open
```

v4.1 新增本地企业治理层，用来把诊断、计划、验证、知识库、控制台和 CI 接入同一个安全边界。

默认策略：

- 只绑定本机地址，默认不开放局域网。
- 不上传原始材料，不启用遥测，不调用外部 API。
- 原始证据访问默认阻断，分享导出默认只允许脱敏材料。
- 敏感操作进入审批流。
- 审计日志采用 append-only JSONL，并进行 hash-chain 校验。

## v4.0 证据绑定推理

```powershell
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor root-cause --input .\report --out .\root_cause_report
failure-doctor causal-chain --input .\report --out .\causal_chain_report
```

确定性诊断仍然是主结论。推理层只能解释和组织证据，不能覆盖高置信度安全阻断结论。每一条 claim 都必须引用 evidence id；证据不足时必须降级为 `insufficient_evidence`。

## 安全边界

Agent Failure Doctor 不是：

- CAPTCHA 绕过工具
- 反爬规避工具
- 账号攻击工具
- 真实平台采集器
- 凭据提取器

项目默认只处理本地、脱敏、授权的失败证据。公开仓库和 PyPI 包不包含本地私有训练题、solver、FLAG、hook、VMP、challenge pass、轨迹生成或隐身配方。

