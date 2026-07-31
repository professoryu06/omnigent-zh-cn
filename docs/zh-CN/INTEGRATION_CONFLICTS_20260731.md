# 三方整合冲突清单（2026-07-31）

本候选版本以 Omnigent upstream `7bdaf78c10e16a26e7fb84c254afa2fa96451ffc`
为代码基线，以 `omnigent-zh-cn` `81594243f7a17303b9ba477b938ac323f938c2e4`
为中文发行层来源。两仓库没有共同 Git 历史，因此本清单采用“文件级选择性移植”，
不做无审计的 merge 或整目录覆盖。

## 已移植

- `web/src/i18n/`：中文/英文词条、语言上下文、词汇表及单元测试。
- `web/src/main.tsx`：挂载 `I18nProvider`，默认中文、可切换英文。
- `docs/zh-CN/`：安装、Windows/WSL2、故障排查及发行交接文档。
- `README.zh-CN.md`、`UPSTREAM.zh-CN.md`：中文入口与同步边界说明。
- `omnigent/cli.py`：Windows 控制台 UTF-8 配置（仅 stdout/stderr，不做全局
  `errors="replace"`）。
- `pyproject.toml`：增加 `omnigent-zh` 与 `omni-zh` 命令别名；仍共用同一
  `omnigent.cli:main`、配置目录和运行时，避免双安装漂移。

## 暂不直接移植

- 当前 review 工作树的 Route-A 代理注入：阶段 24 full-run 尚未成功，不能把
  未验证的代理行为作为候选版本默认路径。
- review 分支中 Codex 隔离、workspace cache、system-prompt fail-loud 等修复：
  这些文件与 upstream runner/server/native 路径存在重叠，须逐文件对照 upstream
  API 后另开移植卡，并由定向测试证明；本候选暂不静默覆盖。
- BUG-1 的 UTF-8/ASCII host 修复已按候选 host/CLI 结构移植。
- BUG-2 的裸 `codex` → SDK、显式 `codex-native` → terminal 路由已由 pinned
  upstream 的 `harness_plugins`/native registry 提供；本候选保留该单一注册表，不
  覆盖成 review 分支的旧 monolithic runner guard。
- BUG-3 的 JSON host launch 已在 upstream；multipart `host_id` 语义已在本候选
  `routes_core.py` 补齐：权限检查、host/workspace 绑定、runner token/frame 和
  单次 launch 共用现有 host-launch helper。
- 中文仓库的整套 `web/src`：其 UI 版本与 upstream v0.7+ 有大量差异，整体替换
  会丢失 upstream 的新组件和生命周期改进。当前先保留 upstream UI，在入口挂载
  可审计的 i18n 层，再按组件清单逐步接入 `useTranslation()`。

## 必须建立的冲突审计

1. `omnigent/cli.py`、`omnigent/host/*`、`omnigent/runner/*`、
   `omnigent/server/*`、`omnigent/inner/*`：先以 upstream 为准，再逐个移植已验证
   修复；每个文件记录来源、测试和回退点。
2. `web/src`：不得以旧中文 fork 覆盖 upstream。每次接入翻译组件必须同时运行
   TypeScript、Vitest 和英文回退测试。
3. `pyproject.toml`/锁文件：保持 upstream 包名和 SDK 版本，中文命令只做别名；
   不引入 `omnigent-zh-cn-*` 依赖，避免与 upstream 生态不兼容。

## 当前结论

候选目录已具备 upstream 基线、中文文档/词条、中文命令入口和 Windows 编码保护，
并已补齐 multipart host launch；尚未宣称“中文 UI 全量完成”或 Gate 通过。后续
必须完成 Codex 隔离移植、Windows/WSL 测试及 Gate 1/2 独立验收。
