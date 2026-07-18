# 上游与许可说明

## 来源

本仓库由 `omnigent-ai/omnigent` 的本地源码快照派生，并加入简体中文界面、中文文档、私有分发命名、安装脚本和跨平台运行指引。

当前工作目录未保留原始 Git 提交历史，因此不能声称与某一个上游 commit 完全对应。首次私有发布会记录本仓库 tag；后续同步上游时必须在独立分支完成差异审查、重新跑测试，并在 release notes 中注明参考的上游 ref。

## 维护范围

- 默认语言为 `zh-CN`，保留 `en` 作为设置内可切换语言。
- Python 分发名称为 `omnigent-zh-cn`；命令为 `omnigent-zh` 和 `omni-zh`。
- Windows 原生仅支持 Web/SDK 模式；完整 tmux 原生 CLI 使用 WSL2。
- macOS 使用 seatbelt；Linux/WSL2 使用 bubblewrap。

## 许可

上游及本仓库采用 Apache License 2.0。发布、分发或继续派生时必须保留根目录的 `LICENSE` 和 `NOTICE`，并不得移除上游版权、第三方声明或商标归属说明。
