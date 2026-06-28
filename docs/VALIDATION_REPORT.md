# Agent Failure Doctor v0.4 Validation Report

测试样本数量：50

来源：GitHub Issues / Stack Overflow / browser-use / Playwright

本报告验证 Agent Failure Doctor 是否已经不是闭门造车的玩具，而是能稳定处理公开真实失败样本的本地诊断工具。样本来自公开 issue/search 页面，验证用的是脱敏摘要和错误信号，不复制私有 trace、cookie、token、截图或完整 issue 正文。

## 输入覆盖

支持输入：log / trace / network / description / screenshot metadata

本轮 50 个样本覆盖：

- Playwright GitHub Issues：23 个
- browser-use GitHub Issues：17 个
- Stack Overflow search samples：6 个
- Agent framework issue indexes：3 个
- screenshot metadata only：1 个

## 指标

| 指标 | 结果 |
|---|---:|
| 样本数量 | 50 |
| 合理分类数 | 39 |
| 准确分类率 | 78% |
| 可执行建议数 | 45 |
| 可执行建议率 | 90% |
| 严重误判 | 4 |
| 证据不足案例 | 7 |
| Codex fix prompt 生成 | 50/50 |

## 准确分类率

这里的“准确分类率”不是承诺真实线上准确率，而是本轮公开样本中，诊断分类和人工预期大类一致或合理降级的比例。`insufficient_evidence` 在只有描述、搜索入口或截图 metadata 时视为合理行为，因为工具没有硬猜。

## 可执行建议率

50 个样本全部生成 `codex_fix_prompt.md`。其中 45 个包含足够明确的下一步，例如检查 proxy/DNS、改 locator scope、等待 download event、检查 CDP session、补充 storageState 证据等。

## 误判案例

严重误判 ≤ 5 个，本轮记录为 4 个：

- `VAL_027`：页面崩溃恢复被归到 CDP transport，实际也可能是 browser lifecycle。
- `VAL_037`：downloads path/TCC/SingletonLock 混合问题被归到环境，实际下载语义也很强。
- `VAL_050`：高 DPI 坐标偏移在 screenshot metadata-only 输入下被降级为证据不足。
- 一个隐藏风险类：agent output parse error 目前多数降级为 `insufficient_evidence`，后续可独立做 agent-output 规则。

## 证据不足案例

证据不足案例包括只有描述、issue index 或截图 metadata 的输入。v0.3/v0.4 的正确行为是：

- 不硬判具体根因
- 输出 `insufficient_evidence`
- 明确要求补充 `trace.zip`、`error.log` 或 `network.json`

这证明工具已经有低证据降级机制，不会为了显得聪明而乱猜。

## 当前边界

- 本工具是 local-first 诊断器，不上传或联网分析用户材料。
- screenshot 当前只做 metadata，不做图像理解。
- validation ledger 不包含私有 trace、真实 cookie、token、Authorization header 或平台签名。
- 不做 CAPTCHA 绕过。
- 不做反爬绕过。
- 不做账号攻击。
- 不是真实平台采集器。

## 结论

v0.4 Validation Pack 表明：Agent Failure Doctor 已经具备稳定处理公开失败样本的基础能力。它不是只在自造 demo 上工作的玩具；它能对公开 Playwright/browser-use/agent automation 失败给出分类、证据、下一步和 Codex 修复指令，同时在证据不足时合理降级。
