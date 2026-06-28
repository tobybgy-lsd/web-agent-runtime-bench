# Community Post Drafts

These drafts are for careful, small-scope sharing after the repository entry is
usable. The goal is not to ask for stars. The goal is to collect sanitized
failure samples from real users.

## English Title

I built a local-first failure doctor for AI browser automation, Playwright, and browser workflow debugging

## Chinese Title

我做了一个本地优先的 AI 自动化失败诊断工具：支持 trace、log、network 和 Codex 修复 Prompt

## Short English Draft

I built Agent Failure Doctor, a local-first tool that diagnoses failed AI browser
automation, Playwright, browser workflow, and RPA runs.

Input:

- trace.zip
- error.log
- console.txt
- network.json
- screenshot metadata
- user_description.txt

Output:

- diagnosis
- evidence
- next action
- repair suggestions
- Codex fix prompt

Please share sanitized failure logs, trace.zip files, or error descriptions if
you have a browser automation failure that is hard to debug. Suitable public
cases may be added to the validation corpus.

Do not include secrets, cookies, tokens, credentials, or private user data.

Safety boundary: this is not a CAPTCHA bypass tool, bot evasion tool, credential
extractor, or unauthorized scraping tool.

## Short Chinese Draft

我做了一个本地优先的 AI 自动化失败诊断工具：Agent Failure Doctor。

它面向 AI Browser Agent、Playwright、RPA 和爬虫脚本失败排查，支持把脱敏后的
trace、log、network、截图 metadata 或失败描述放进本地文件夹，然后生成：

- 失败诊断
- 证据链
- 下一步动作
- 修复建议
- 可以交给 Codex 的修复 Prompt

我现在最需要的不是 star，而是真实但脱敏的失败样本。

欢迎提交脱敏后的失败日志、trace.zip 或错误描述，我会把适合公开的案例加入
validation corpus。

请不要提交密码、API key、cookie、token、授权头、私密截图或个人数据。

边界：它不是验证码绕过工具，不做 bot evasion，不提取凭据，也不服务于未授权采集。

## Places To Share Later

- GitHub README
- GitHub Discussions: Failure Cases
- V2EX
- Juejin
- Reddit r/Playwright
- Reddit r/webscraping
- Hacker News Show HN
