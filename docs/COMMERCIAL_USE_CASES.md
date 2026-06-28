# Commercial Use Cases

Agent Failure Doctor 的商业化基础不是“更多 failure type”，而是让团队更快定位 AI 自动化、RPA、Playwright/E2E 和内部脚本失败的下一步动作。

## 1. AI Agent 调试助手

面向 Browser Agent、computer-use agent、workflow agent 开发团队。用户把 trace、log、network、截图 metadata 或失败描述放进本地文件夹，工具输出：

- 人话结论
- 证据链
- 下一步
- Codex/Claude 修复指令

价值：减少 agent 失败后的人工排查时间。

## 2. RPA 故障排查工具

面向运营自动化和企业 RPA 维护。常见问题包括按钮找不到、页面没加载完、下载没保存、弹窗/遮罩阻塞、浏览器环境不一致。

价值：让非底层工程人员也能拿到可交给开发者的结构化报告。

## 3. Playwright/E2E 测试失败诊断

面向 QA、测试平台和前端工程团队。工具可以先于 Trace Viewer 手动排查，给出 failure type、evidence、repair suggestions 和 issue draft。

价值：把散落的 trace/log/network 证据整理成可执行修复任务。

## 4. 企业内部自动化脚本维护工具

面向大量内部脚本、定时任务、报表导出和浏览器自动化流程的团队。

价值：把“脚本又挂了”变成标准诊断包，便于值班、交接和后续修复。

## 明确不做

- 不是 CAPTCHA 绕过
- 不是反爬绕过
- 不是账号攻击工具
- 不是真实平台采集器
- 不提取 Cookie、Token、Authorization 或密码
- 不帮助规避网站访问控制

## 适合的交付形态

- 开源 CLI 工具
- 企业内部诊断脚本
- CI 失败报告增强器
- 私有 Web UI 上传诊断器
- Codex/Claude 修复指令生成器
