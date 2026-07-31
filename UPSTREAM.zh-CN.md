# 上游来源与同步策略

## 来源与定位

本仓库是基于 [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent) 的**完整源码发行版**。它包含 Omnigent 核心、Web UI、SDK 与中文化改动；安装 `omnigent-zh-cn` 后无需再安装官方 Omnigent。

本仓库不是官方项目，也不代表官方支持渠道。Omnigent 的名称、商标、版权和第三方声明归其原始作者与贡献者所有。

## 维护范围

- Web UI 默认语言是 `zh-CN`，仍保留 `en` 作为设置中的可选语言。
- Python 分发名是 `omnigent-zh-cn`；命令仅为 `omnigent-zh` 和 `omni-zh`，不覆盖官方命令。
- Windows 原生支持 Web/SDK 模式；完整 tmux 原生 CLI 协作以 WSL2 为官方路径。
- macOS 使用 seatbelt；Linux/WSL2 使用 bubblewrap。
- 根目录 `LICENSE`、`NOTICE` 与上游版权声明必须保留。

## 上游联动机制

`.github/workflows/upstream-watch.yml` 每周查询上游默认分支，也支持手动触发。发现新的上游 revision 时，它会创建或更新带 `upstream-sync` 标签的 Issue。

该工作流只负责提醒，**绝不自动 merge 或 push**。原因是上游更新可能同时影响中文词典、平台能力提示、独立包名、CLI 命令、发布审计和 Web 测试。

## 人工同步流程

1. 在新分支添加上游远端：

   ```bash
   git remote add upstream https://github.com/omnigent-ai/omnigent.git
   git fetch upstream
   ```

2. 对照 `upstream-sync` Issue 的 revision 审查变更：

   ```bash
   UPSTREAM_BRANCH=$(gh api repos/omnigent-ai/omnigent --jq .default_branch)
   git diff --stat main..upstream/$UPSTREAM_BRANCH
   git diff main..upstream/$UPSTREAM_BRANCH -- web/src/i18n omnigent pyproject.toml
   ```

3. 分批引入需要的上游改动，并保留以下本仓库边界：
   - `web/src/i18n/locales/zh-CN.ts` 与中文化测试。
   - `omnigent-zh-cn`、`omnigent-zh`、`omni-zh` 的分发与入口命名。
   - Windows/WSL2/macOS 平台提示、安装脚本与发布审计。

4. 运行发布审计、后端测试、前端构建与三平台 CI；记录参考的上游 revision。

5. 通过审查后合并并创建新的 `v*-zhcn.*` tag。

## 许可

上游与本仓库均遵循 Apache License 2.0。任何再发布或派生都必须保留根目录的 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。
