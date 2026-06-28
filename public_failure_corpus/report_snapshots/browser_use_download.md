# Agent Failure Diagnosis

## 结论

这个失败更像是 **文件上传下载失败**。
- 技术分类：`playwright_download`
- 子类型：`download_event`
- 修复难度：`easy`

## 证据

- download marker found: download
- download event fired but file was not persisted

## 为什么

为什么不是其他分类：页面动作可能已经触发成功，缺的是下载事件等待、`acceptDownloads` 或 `saveAs` 持久化流程。

## 下一步

- 在触发下载的动作周围等待 download event。
- 启用或检查 `acceptDownloads`。
- 用 `download.saveAs(...)` 保存文件。

## 给 Codex 的修复指令

要求 Codex 包住下载动作、保存文件、增加断言，并保留失败时的日志和下载路径。
