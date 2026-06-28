# Agent Failure Doctor

[English documentation](README.md)

Agent Failure Doctor 是一个本地优先的 AI 自动化失败诊断工具，面向 AI Browser Agent、Playwright、RPA、爬虫自动化和数据采集脚本调试。

输入：
trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt

输出：
diagnosis、evidence、next action、repair suggestions、GitHub issue draft、Codex fix prompt。

快速开始：

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m pip install -e .
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

## 安全边界

本项目只做本地脱敏材料诊断，不上传 trace、日志、cookie、token、网络包或截图。

本项目不是：

- CAPTCHA 绕过工具
- bot evasion 工具
- 指纹伪造工具
- 动态签名破解工具
- 账号攻击工具
- 未授权采集工具
- 真实平台采集器
- 反风控绕过工具

如果疑似遇到访问限制或风控，工具只会给出识别、分流和合规建议，例如使用官方 API、确认授权、降低访问量、联系平台或停止未授权采集。

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

不要提交密码、cookie、token、authorization header、API key、私有 URL、个人数据或客户数据。
