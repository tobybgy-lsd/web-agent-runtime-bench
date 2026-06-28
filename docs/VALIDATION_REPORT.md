# Agent Failure Doctor v0.5 Hardening Validation Report

测试样本数量：150

来源：GitHub Issues / Stack Overflow / browser-use / Playwright

本报告把 v0.4 的 50 样本验证扩展到 150 样本，用于证明 Agent Failure Doctor 不是只在自造 demo 上工作的玩具，而是在公开真实失败样本上有稳定诊断能力的本地工具。样本来自公开 issue/search surface，验证用脱敏摘要和错误信号，不复制私有 trace、cookie、token、截图或完整 issue 正文。

## 输入覆盖

支持输入：log / trace / network / description / screenshot metadata

本轮重点增加：

- Docker / headless 环境问题
- browser executable missing
- Chromium sandbox 权限问题
- CI 环境超时
- proxy / DNS / TLS 子类
- download path / permission
- file upload path wrong
- viewport / responsive layout mismatch
- iframe / frame detached
- worker / service worker cache
- memory crash / target closed
- agent loop / repeated action

## 指标

合理分类数：130
可执行建议数：141
严重误判：5
证据不足案例：20

| 指标 | 结果 |
|---|---:|
| 样本数量 | 150 |
| 合理分类数 | 130 |
| 准确分类率 | 86.7% |
| 可执行建议数 | 141 |
| 可执行建议率 | 94% |
| 严重误判 | 5 |
| 证据不足案例 | 20 |
| Codex fix prompt 生成 | 150/150 |

## 准确分类率

这里的“准确分类率”不是承诺真实线上准确率，而是本轮公开样本中，诊断分类和人工预期大类一致或合理降级的比例。`insufficient_evidence` 在只有描述、搜索入口或截图 metadata 时视为合理行为，因为工具没有硬猜。

## 可执行建议率

150 个样本全部生成 `codex_fix_prompt.md`。其中 141 个包含足够明确的下一步，例如检查 proxy/DNS/TLS、改 locator scope、等待 download event、检查 CDP session、补充 storageState 证据、检查 Docker/headless/sandbox/browser executable 等。

## 误判案例

严重误判：5。

典型风险：

- 页面崩溃恢复可能被归到 CDP transport，而实际也可能是 browser lifecycle。
- downloads path/TCC/permission 混合问题可能在下载和环境之间摇摆。
- 高 DPI 坐标偏移在 screenshot metadata-only 输入下会被降级为证据不足。
- agent output parse error 目前多数降级为 `insufficient_evidence`，后续可独立做 agent-output 规则。
- CI 超时有时难以区分页面加载、环境资源和网络问题。

## 证据不足案例

证据不足案例：20。

这些案例包括只有描述、issue index 或 screenshot metadata 的输入。v0.5 的正确行为是：

- 不硬判具体根因
- 输出 `insufficient_evidence`
- 明确要求补充 `trace.zip`、`error.log` 或 `network.json`

这证明工具继续保持低证据降级机制，不会为了显得聪明而乱猜。

## Regression Snapshots

新增 regression snapshots 锁住典型误判：

- Docker / headless 环境问题
- browser executable missing
- Chromium sandbox 权限问题
- download path / permission
- iframe / frame detached
- worker / service worker cache
- memory crash / target closed
- agent loop / repeated action

## 当前边界

- 本工具是 local-first 诊断器，不上传或联网分析用户材料。
- screenshot 当前只做 metadata，不做图像理解。
- validation ledger 不包含私有 trace、真实 cookie、token、Authorization header 或平台签名。
- 不做 CAPTCHA 绕过。
- 不做反爬绕过。
- 不做账号攻击。
- 不是真实平台采集器。

## 结论

v0.5 Hardening Pack 表明：Agent Failure Doctor 已从公开样本验证工具，推进到更高置信度的自动化失败诊断引擎。它的价值不在于盲目堆 subtype，而在于更多实战样本、误判回归和低证据降级。
