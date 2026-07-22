# 核心候选修复方案（修订版）

> 目标：在**可复现证据**下，修复身份、路由、隔离、组合与长任务可用性。  
> 每个 issue：方案 A（L0）/ B（L1 功能）/ C（L2 上游完整契约）。  
> **「已修复」必须以测试证据为准。**

---

## #2853 Native harness 静默丢弃 `prompt:` / `system_prompt`

### 功能目标

禁止静默丢弃。契约统一为：

| 模式 | 含义 |
|------|------|
| **apply** | 已证实该 harness 有**安全且受支持**的传递通道时注入 |
| **warn** | 不支持或通道不安全时**明确告警**（不得静默） |
| **error** | `strict_prompt` 或关键角色要求时 **fail-fast** |

第一阶段**最低可接受修复**：禁止静默丢弃（warn 或 error）。  
**不能**在未证明安全传递前，对所有 native 做同一注入。

### 逐 harness 能力矩阵（实施前必填；未填 = 不得 apply）

| Harness | 传递通道候选 | argv 泄露风险 | 本轮验证结果 | 策略 |
|---------|--------------|---------------|--------------|------|
| claude-native | `--append-system-prompt` / session settings | 若走 argv 需评估 | 待测 | apply 仅当安全通道确认 |
| codex-native | session create / app-server instructions | TBD | 待测 | 同上 |
| cursor-native | TBD | TBD | 待测 | warn 直至确认 |
| hermes-native | TBD | TBD | 待测 | warn 直至确认 |
| opencode-native | session-init（文档称 aspirational） | TBD | 待测 | warn 直至确认 |
| goose-native / kimi / kiro / qwen / antigravity / pi-native / native_server_harness | 见源码 `del system_prompt` | TBD | 待测 | 默认 warn；strict → error |

**注意：** 敏感 prompt **不得**默认暴露在可被进程列表读取的 argv，除非有明确安全设计。

### 方案 A — L0

- 关键角色改用 SDK / 已证实会 apply 的 harness；或把纪律写入仓库内强制读取的协议文件（非 system_prompt 通道）。
- **不**声称 native 身份问题已解决。

### 方案 B — L1（与 C 对齐，非「仅 warn」）

1. 建矩阵 + capture double 测试（sentinel 是否到达承诺通道）。  
2. 实现共同 **fail-loud**：非空 system_prompt + native 且未 apply → warning；`strict_prompt` → error。  
3. 仅对矩阵中 **apply 已证实且安全** 的 harness 实现注入。  
4. 不假设各 CLI prompt 语义相同。

### 方案 C — L2 上游完整

- 正式 `HarnessPromptDelivery` 契约（apply|warn|error）+ 文档 + 各 harness 适配器。  
- **方案 C 不是单纯 warn-only**；warn 是不支持路径的合规输出，apply 是支持路径的目标行为。

### 分支

`fix/core-2853-native-prompt`（独立 PR）

### 自动化断言

- 唯一 sentinel 字符串；**capture double** 断言通道。  
- **不以**「模型是否碰巧写 commit trailer」为唯一断言。

---

## #3016 失败 snapshot 毒化 workspace 投影缓存

### 功能目标

- 仅当 snapshot **成功**且结果可信时写入 `_session_workspace_cache`。  
- 失败不得 memoize `workspace=None`。  
- `reset-agent-cache` 驱逐相关 projection cache（含 workspace）。  
- 注意：若 harness 已在错误 cwd 下 bake env 启动，仅修缓存不够；需定义是否强制重建进程 / 文档化「须重建 session」。

### 方案 A — L0

- 运维：cwd 异常 → 删 session；避免抖动时狂刷 filesystem。  
- Runbook，非根治。

### 方案 B — L1（推荐首修）

- `_session_workspace_value` / `_ensure_session_registered`：失败不写 workspace 缓存。  
- `_clear_session_agent_caches`：pop workspace（及必要的投影缓存）。  
- 测试：第一次非 200 → 第二次 200 + 有效 workspace → cwd 为 worktree。

### 方案 C — L2

- 缓存分层 invalidation 与 harness env bake 生命周期统一文档。

### 分支

`fix/core-workspace-3016`

---

## #2747 单文件 YAML 忽略 `type`/`config` 嵌套

### 功能目标

单文件 `executor:` 中声明的 harness **不得**被静默丢弃后改由 model-prefix 推断顶替。

### 规范与代码（实施前核对，禁止发明优先级）

上游 issue 指向：`omnigent/inner/loader.py` → `_parse_executor_spec` 只读 `model|harness|profile|auth`。  
bundle 形态使用 `type: omnigent` + `config.harness`。  
`omnigent/spec/omnigent.py` 中 harness 解析另有文档化 precedence（flat harness → parent → model infer）。

**单文件路径目标（在复现确认后）：**

- 接受 flat：`executor.harness`  
- 或接受 alias：`executor.config.harness`（若选择兼容）  
- 或对未知键 `type`/`config` **响亮报错**并提示 flat 拼写  
- 仅在**未声明任何 harness**时允许 model-prefix inference  

### 方案 A — L0

- 文档/示例统一 flat 拼写；CI 检查关键角色 YAML。

### 方案 B — L1

- 改 loader；**独立 commit + 独立测试**（可与 #2746 同 PR，但提交分离）。  
- 若 diff 横跨无关 loader/executor 过大 → 拆 PR。

### 分支

`fix/core-spec-parse-2746-2747` 或拆分

---

## #2746 codex-native 读错 model 字段

### 功能目标

`_codex_native_model_from_spec` 与 `_resolve_spec_model` / 其他 native 对齐：优先 `spec.executor.model`，可 fallback `config["model"]`。

### 方案 A — L0

- 启动时 session `model_override`；或 CLI `--model`。

### 方案 B — L1

- 改 `_codex_native_model_from_spec`；独立测试。

### 与 #2747

- 同 PR 允许，**独立提交、独立回归**。

---

## #2854 harness_override 与 kickoff

### 方案 A

- 先空 session 再 kickoff（编排层封装）。

### 方案 B

- create 路径 turn0 与后续共用 override。

### 复现

C-2854：create + override + initial_items → turn0 harness == override。

---

## #2539 named 子会话 404

### 方案 B

- 稳定 session↔agent 查找；禁无序 `LIMIT 1` 破坏单所有者。

### 复现

C-2539：同 parent ≥3 named children。

---

## #2967 无 auto-compact

### 方案 A

- 关卡轮换 session + 摘要（运维能力，非 compact 根治）。

### 方案 B

- turn 路径 proactive / reactive compact；边界：单条过大、compact 失败。

### 复现

C-2967：主动 compact、overflow 后单次 retry、过大输入、compact 失败。

---

## 验收：Markdown checklist ≠ 可运行矩阵

见 `scripts/repro/`：固定基线 SHA、环境、命令、故障注入、断言、超时、产物路径。  
每个用例记录：upstream/zh-cn commit、OS/Python/Omnigent 版本、命令、预修复结果、修复后结果、日志位置。
