# HERMES_REVIEW_26 — CODEX_TASK_24 修复准备度只读审查

**RUN_ID**: `20260731-130500-dc83140-hermes-review26-r1`
**日期**: 2026-07-31
**角色**: Hermes 只读审查，不修改源码
**目标**: 审查 CODEX_TASK_24 的 Codex CLI 隔离与 TUN 代理修复是否具备进入一次 full-run 的条件

---

## 0. 审查结论（先行）

**不具备进入 full-run 的条件。**

原因：
1. **方案 D 双路回退未在工作树中实施**。当前代码只有 Route A（child env 代理注入 + config overrides），没有 WSL native fallback 路径。
2. **Route A 已被 CODEX_TASK_24_PLAN.md 第 10 节明确标记为"not accepted as a fix"**：四次 full-run（r1-r4）全部失败，错误为 Rust 10106/11003；in-process probe 也失败。
3. 隔离契约本身完整且测试全绿，但网络层问题未解决，full-run 无法产出 `CONTROLLER_OK`。

---

## 1. OpenCodex 隔离审查

| 检查项 | 状态 | 证据 |
|--------|------|------|
| `~/.codex/config.toml` 未被修改/删除 | ✅ PASS | git diff 无该文件变更 |
| OpenCodex 进程存活 | ✅ PASS | PID 12248 监听 127.0.0.1:10100（PID 从 15536 变为 12248，端口仍活） |
| 10100 未被释放/占用 | ✅ PASS | netstat 确认 LISTENING |
| 私有 CODEX_HOME | ✅ PASS | `codex_executor.py:1377` `_populate_codex_home_config` 使用每会话私有目录 |
| tomlkit 清洗（移除 openai_base_url/model） | ✅ PASS | `_sanitise_codex_config` (line 221) 移除 `_CODEX_CONFIG_POLLUTION_KEYS` |
| 10100 endpoint 阻断 | ✅ PASS | `_CODEX_CONFIG_FORBIDDEN_ENDPOINT = "127.0.0.1:10100"`，清洗后仍含则 raise |
| auth.json 桥接 | ✅ PASS | 只读 symlink，不打印内容 |
| 模型固定 gpt-5.6-sol | ✅ PASS | `-c model="gpt-5.6-sol"` argv override (line 2315+) |
| env denylist（OPENAI_BASE_URL/OPENAI_API_BASE） | ✅ PASS | `_CODEX_ENV_DENY_EXACT` (line 126) |
| gateway/订阅互斥 | ✅ PASS | line 2315-2322 raise OSError |
| 不连接 10100 | ✅ PASS | r1-r4 evidence 均确认 `connected_10100=false` |

**隔离契约结论**: 完整，无回归。25 个隔离测试全绿。

## 2. 代理/TUN 路径审查

### 2.1 Route A 实现状态

| 检查项 | 状态 | 代码位置 |
|--------|------|----------|
| `OMNIGENT_CODEX_PROXY` 环境变量 | ✅ 已实现 | `codex_executor.py:152` |
| 默认代理 `http://127.0.0.1:7897` | ✅ 已实现 | `_CODEX_DEFAULT_PROXY` (line 153) |
| 代理 scheme 校验（http/https/socks5/socks5h） | ✅ 已实现 | `_CODEX_PROXY_SCHEMES` (line 154) |
| 禁止 direct/none/off/disabled | ✅ 已实现 | `_resolve_codex_proxy` (line 172) |
| 禁止嵌入凭据 | ✅ 已实现 | line 191-194 |
| 6 个代理变量全部注入（HTTP_PROXY/HTTPS_PROXY/ALL_PROXY 大小写） | ✅ 已实现 | `_CODEX_PROXY_ENV_KEYS` (line 155-162) |
| NO_PROXY 保留 127.0.0.1,localhost | ✅ 已实现 | `_CODEX_LOCAL_NO_PROXY` (line 163) |
| config override `features.network_proxy=true` | ✅ 已实现 | line 2311 |
| config override `network_proxy.proxy_url=<url>` | ✅ 已实现 | line 2312 |
| gateway 模式排除代理注入 | ✅ 已实现 | `if not gateway:` (line 2307) |
| host/connect.py 转发 OMNIGENT_CODEX_PROXY | ✅ 已实现 | `connect.py:366` |

### 2.2 Route A 实际效果

**四次 full-run 全部失败**（CODEX_TASK_24_PLAN.md 第 10 节）：

| RUN | 错误 | 10100 连接 | OpenCodex |
|-----|------|-----------|-----------|
| r1 (152542) | Rust 10106/11003 | 无 | 存活 |
| r2 (153045) | Rust 10106/11003 | 无 | 存活 |
| r3 (153704) | Rust 10106/11003 | 无 | 存活 |
| r4 (154130) | Rust 10106/11003 | 无 | 存活 |

**in-process probe 也失败**：同一 native binary + 代理，无法产出 `turn/completed`。

**结论**: Route A 代码实现正确，但 **Codex CLI 0.146.0 的 Rust 网络栈不读取或不正确使用注入的代理变量/config overrides**。代理注入没有改变 CLI 的实际出站路径。

### 2.3 方案 D 双路回退

**未在工作树中实施**。

搜索范围：
- `omnigent/inner/codex_executor.py`：无 WSL/dual-path/fallback 逻辑
- `omnigent/inner/codex_harness.py`：无变更
- `omnigent/runner/_entry.py`：只有 graceful shutdown 改动，无 WSL 路由
- `omnigent/runner/app.py`：无 WSL/dual-path 逻辑
- `omnigent/inner/loader.py`：只有 bundle-key 校验，无路由选择
- 全仓库 grep `wsl|WSL|dual.path|fallback.*native|route.*D`：无匹配（排除无关的 WSL2 提示文本）

**WSL 基础设施状态**（docs/fixes/WSL_REPAIR_20260731.md）：
- Ubuntu-24.04 已恢复可用
- Python 3.12.3, uv 0.11.33, Node v22.23.1, tmux 3.4, bwrap 0.9.0
- **Codex CLI 版本为 0.144.4**（不是 0.146.0）
- 新版 WSL 入口：`C:\Program Files\WSL\wsl.exe`

**WSL 代理桥接**（docs/fixes/WSL_PROXY_BRIDGE_20260731.md）：
- `172.31.80.1:17892 -> 127.0.0.1:7897`（已改为当前 Clash Verge 端口）

### 2.4 TUN/代理环境

| 检查项 | 状态 |
|--------|------|
| TUN 未关闭 | ✅ |
| TUN 模式未切换 | ✅ |
| 未设 DIRECT | ✅ |
| 未执行 netsh winsock reset | ✅ |
| 7897 存活 | ✅ PID 4836 监听 |
| Clash Verge 配置未改 | ✅ gvisor + fake-ip |

## 3. CLI 固定审查

| 检查项 | 状态 | 值 |
|--------|------|-----|
| path | ✅ | `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe` |
| version | ✅ | 0.146.0 |
| size | ✅ | 358650672 |
| SHA-256 | ✅ | `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` |
| SHA match | ✅ | True |
| HARNESS_CODEX_PATH 继承链 | ✅ | `codex_harness.py:112` → `_CodexAppServerSession` → argv[0] |
| 未走 codex-native terminal/tmux | ✅ | harness=codex, module=omnigent.inner.codex_harness |
| 240s idle watchdog 未修改 | ✅ | 无相关 diff |

## 4. 回归测试

| 套件 | 结果 | 说明 |
|------|------|------|
| `tests/inner/test_codex_runtime_isolation.py` | **25 passed** ✅ | 隔离契约全绿 |
| `tests/test_harness_dispatch.py` | **4 passed** ✅ | |
| `tests/runner/test_codex_terminal_ensure_guard.py` | **3 passed** ✅ | |
| `tests/server/test_multipart_host_launch.py` | **4 passed** ✅ | |
| `tests/host/test_connect.py` | **71 passed, 2 skipped** ✅ | Windows 路径债务已修复（CODEX_TASK_25） |
| `tests/cli/test_backend.py` | **69 passed, 1 failed** ⚠️ | 见下 |

### test_backend.py 唯一失败

`test_claude_command_routes_server_through_ensure_backend`：
- 错误：`omnigent-zh claude` 需要 tmux/PTY，Windows 原生模式不支持
- **分类**: pre-existing Windows 平台限制，与 CODEX_TASK_24 无关
- 不是隔离修复引入，不是代理注入引入

### 失败分类汇总

| 分类 | 数量 | 说明 |
|------|------|------|
| 本任务相关失败 | **0** | 无 |
| 历史/环境失败 | **1** | tmux/PTY Windows 限制 |
| 非本任务改动导致 | **0** | 无 |

## 5. 方案 D 实施缺口分析

用户确认"Codex 已实施方案 D 双路回退"，但工作树中不存在该实施。可能原因：

1. **实施在另一个 worktree/分支**：当前分支 `docs/fix-plans-core-secondary`，HEAD `dc83140`，无 stash，无其他本地分支包含该代码。
2. **实施尚未同步到本工作树**：Codex 可能在另一个环境完成，代码未 push/merge 到此处。
3. **实施被回滚或未保存**：四次 Route A 失败后可能未继续。

### 方案 D 预期实现（基于用户描述）

| 组件 | 预期 | 当前状态 |
|------|------|----------|
| Windows native 路径（Route A 代理） | 保留，先尝试 | ✅ 已实现 |
| WSL native fallback | 代理失败时自动切换 WSL 内 Codex CLI | ❌ 未实现 |
| 路由选择逻辑 | `codex_executor.py` 或 `codex_harness.py` 中检测代理失败 → 切 WSL | ❌ 未实现 |
| WSL Codex CLI 版本 | 需固定（当前 WSL 内为 0.144.4，不是 0.146.0） | ⚠️ 版本不一致 |
| WSL 代理桥接 | `172.31.80.1:17892 -> 127.0.0.1:7897` | ✅ 已配置 |
| 测试覆盖 | 双路回退测试（代理成功/失败/WSL fallback） | ❌ 未实现 |

## 6. full-run 准备度判定

### 判据清单

| 判据 | 状态 | 说明 |
|------|------|------|
| 隔离契约完整 | ✅ | 25 tests passed |
| CLI identity 固定 | ✅ | SHA match |
| OpenCodex/10100 不受影响 | ✅ | PID 12248 存活 |
| TUN 未改 | ✅ | |
| 代理注入代码正确 | ✅ | Route A 实现无 bug |
| **代理注入实际生效** | ❌ | 四次 full-run 证明 CLI 不走代理 |
| **方案 D 双路回退已实施** | ❌ | 工作树中无代码 |
| **WSL fallback 可用** | ❌ | 无路由逻辑，WSL CLI 版本不一致 |
| 回归测试无本任务失败 | ✅ | 0 个相关失败 |
| leak-scan | N/A | 未跑 full-run，无新 evidence |

### 最终判定

**❌ 不具备进入 full-run 的条件。**

- Route A 单独不可用（四次失败已证明）
- 方案 D 未实施，无 fallback 路径
- 即使现在跑 full-run，预期结果仍是 Rust 10106/11003 失败

## 7. 建议下一步

### 给 Codex/Grok 的实施卡

```
你是 Codex/Grok，负责实施 CODEX_TASK_24 方案 D 双路回退。

工作树：F:\codex-ai\git项目部署\tmp\omnigent-review

先读：
1. docs/fixes/handoffs/HERMES_REVIEW_26.md（本审查）
2. docs/fixes/handoffs/CODEX_TASK_24_PLAN.md（第 10 节 Route A 失败记录）
3. docs/fixes/WSL_REPAIR_20260731.md（WSL 基础设施状态）
4. docs/fixes/WSL_PROXY_BRIDGE_20260731.md（代理桥接）
5. omnigent/inner/codex_executor.py（Route A 实现，line 148-218, 2296-2314）

实施要求：

1. 在 codex_executor.py 或 codex_harness.py 中增加路由选择：
   - 默认走 Windows native + Route A 代理
   - 如果代理路径失败（检测 10106/11003/timeout），自动切换 WSL fallback
   - 或者提供 OMNIGENT_CODEX_ROUTE=auto|windows|wsl 配置

2. WSL fallback 实现：
   - 使用新版入口 C:\Program Files\WSL\wsl.exe
   - 固定 Ubuntu-24.04
   - WSL 内 Codex CLI 需升级到 0.146.0 并固定 SHA（当前为 0.144.4）
   - WSL 内代理：172.31.80.1:17892 -> 127.0.0.1:7897（已配置）
   - WSL 内 CODEX_HOME 使用私有目录，auth.json 桥接
   - 模型固定 gpt-5.6-sol

3. 测试：
   - 新增双路回退测试（代理成功/失败/WSL fallback/WSL 不可用）
   - 复跑 tests/inner/test_codex_runtime_isolation.py（25 passed 基线）
   - 复跑 tests/test_harness_dispatch.py + test_codex_terminal_ensure_guard.py

4. full-run：
   - 新 RUN_ID/evidence
   - 成功判据：CONTROLLER_OK + turn/completed + C exit=0 + 无 10100 + OpenCodex 存活
   - 如果 Windows native 失败但 WSL fallback 成功，记录切换证据

约束：
- 不改 ~/.codex/config.toml
- 不杀 OpenCodex，不动 10100
- 不改 TUN/Meta
- 不改 240s watchdog
- 凭据 [REDACTED]
- 不 commit/push/merge（除非任务卡授权）
- 完成后按 AGENTS.md 四维格式输出报告
```

## 8. Gate 边界声明

- 本审查**不是** Gate 2 验收
- Gate 1 仍为"相对 main PASS"（test_connect.py 修复后可升级为绝对 PASS）
- Gate 2 仍为 **NOT PASS**，不可 merge
- 即使方案 D 实施后单次 full-run 通过，也只代表隔离链路 + 网络路径通过
- Gate 2 六轮独立验收仍须完成

## 9. Evidence 文件清单

| 文件 | 内容 |
|------|------|
| 本文档 | `docs/fixes/handoffs/HERMES_REVIEW_26.md` |
| Route A evidence | `C:\Users\Administrator\omnigent-diagnostics\20260731-15*-codex-proxy-fullrun-r[1-4]\` |
| 诊断 evidence | `C:\Users\Administrator\omnigent-diagnostics\20260731-064535-dc83140-hermes-diag24-r1\` |
| WSL 修复记录 | `docs/fixes/WSL_REPAIR_20260731.md` |
| WSL 代理桥接 | `docs/fixes/WSL_PROXY_BRIDGE_20260731.md` |
| CODEX_TASK_24_PLAN | `docs/fixes/handoffs/CODEX_TASK_24_PLAN.md`（第 10 节） |
