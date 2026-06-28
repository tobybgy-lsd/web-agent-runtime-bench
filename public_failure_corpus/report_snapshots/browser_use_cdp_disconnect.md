# Agent Failure Diagnosis

## 结论

这个失败更像是 **浏览器环境不一致**。
- 技术分类：`cdp_websocket_disconnected`
- 子类型：`websocket_disconnect`
- 修复难度：`hard`

## 证据

- CDP WebSocket marker
- httpx.ReadError marker
- browser session transport instability

## 为什么

为什么不是其他分类：失败发生在 CDP/session transport 层，页面 selector 或业务页面状态不是第一嫌疑。

## 下一步

- 记录浏览器进程、CDP 连接生命周期和断线时最后一步动作。
- 对远程浏览器 session 增加 fail-fast 或 bounded reconnect。

## 给 Codex 的修复指令

要求 Codex 加 session health check、CDP 日志和有上限的重连，不要把它误修成等待 selector。
