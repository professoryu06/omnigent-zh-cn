# GROK GATE 2 POLICY REVIEW — AC-4/5/6 与 codex-native Phase 2 正向 apply 校准

**审查者：** Grok（Gate 2 契约审查者；本阶段**不**执行 smoke）  
**日期：** 2026-07-29  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_8.md`  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`（只读核对；未改政策/源码/测试）

---

## 0. 状态边界（必须先读）

| 项 | 状态 |
|----|------|
| Gate 1 | **PASS（相对 main）**（Codex 已判定；见 r6 / 分类证据） |
| Gate 1 含义 | **不等于**全仓 GREEN；candidate 全仓仍非 exit 0 |
| Gate 2 | **未执行、未判定** |
| Merge | **不可 merge** |
| 本阶段 | 只读契约核对 + 最小 C/E/R 矩阵设计；**未**跑 pytest / Ruff / Gate / CLI smoke；**未**启停 host/server/tmux；**未**改 `PRE_MERGE_GATES.md` / 源码 / tests / STATUS / 旧 handoff；**未** commit/push/merge/tag |

本报告**不**签发 Gate 2 PASS，**不**批准合并。

---

## 1. 结论摘要

### 1.1 冲突认定（不可模糊）

**是：当前 `PRE_MERGE_GATES.md` §2 的 AC-4 / AC-5 若绑定到「Executor = fresh codex-native」同一会话，与阶段 5 已落地并经阶段 6 接受的 Phase 2 正向 apply 契约直接冲突。**

依据：

| 侧 | 契约行为 |
|----|----------|
| **现行 Gate 2 模板**（§2.1–2.3） | Executor 示例 harness = `codex-native`；步骤 4–5 要求同一 Executor 路径上出现 fail-loud **warning**（AC-4）与 `OMNIGENT_STRICT_PROMPT=1` **注入前失败**（AC-5） |
| **阶段 5 Phase 2** | fresh、非 fork 的 `codex-native` 写入私有 `CODEX_HOME/config.toml` 顶层 `developer_instructions` + digest receipt；receipt 匹配时 `applied=True` → **无 warning**；strict 下 **继续** turn/start |
| **互斥** | 不能用**同一个** fresh codex-native session 同时证明「已 apply」与「未 apply / fail-loud」 |

AC-2 / AC-3（harness/model 未被替换）与 Phase 2 **不冲突**，应保留在 E-positive。  
AC-6（禁止无证据声称送达）**方向正确**，但需收紧为：仅完整 Phase 2 证据链才可声称 **codex-native fresh 已送达**；其它 native **永远不得**声称送达。

### 1.2 校准原则（不放宽 Gate）

把证据拆成两条互不混用的路径：

1. **Phase 2 正向（E-positive）**：fresh 非 fork `codex-native` → receipt 匹配 → 无 fail-loud warning → strict 可继续 → 真实短回复 + harness/model 断言。  
2. **Phase 1 负向（E-negative）**：明确无 apply 通道的 native（推荐）或隔离的 receipt-mismatch 控制 → non-strict warning（`chars=N`，无正文）+ 独立 strict 会话注入前失败。

### 1.3 本阶段交付

- 仅新建本文件。  
- 给出 §3 八问逐项是/否 + 依据。  
- 给出可转写为后续执行卡的最小 C/E/R 实机矩阵与命令/证据模板。  
- 给出 `PRE_MERGE_GATES.md` §2 **最小逐字修订建议**（**未**实际修改政策）。

---

## 2. 阶段 5 / 6 已接受行为（只读摘要）

| 来源 | 要点 |
|------|------|
| `GROK_COMPLETION_5_REWORK.md` | receipt 四项匹配；start 先 `clear_prompt_receipt`；仅 private config 成功后写 receipt；仅 true fresh 非 fork 传 `developer_instructions` |
| `HERMES_REVIEW_6.md` | **approve**；Phase 1 覆盖 11 harness；Phase 2 仅 codex-native fresh 非 fork；其余 10 个仅 fail-loud |
| 生产代码 | 见 §3 行号 |

能力矩阵（`omnigent/inner/native_prompt_delivery.py` L36–48）：

- `codex-native` → `"apply"`  
- 其余 10：`claude-native` / `cursor-native` / `hermes-native` / `opencode-native` / `goose-native` / `kimi-native` / `kiro-native` / `qwen-native` / `antigravity-native` / `pi-native` → `"warn"`

---

## 3. 任务卡八问（是/否 + 精确依据）

### Q1. fresh、非 fork codex-native receipt 匹配时，`applied` 是否为 true？

**是。**

| 依据 | 位置 |
|------|------|
| Executor 读 receipt 并匹配 | `omnigent/inner/codex_native_executor.py` L202–212：`_applied = receipt_matches_prompt(_receipt, system_prompt)` → `note_native_system_prompt(..., applied=_applied)` |
| Matcher 四项全过才 True | `native_prompt_delivery.py` L167–183：`harness_id==codex-native`、`channel==codex_home_config_toml`、`chars==len(prompt)`、`sha256` 匹配 |
| Fresh 非 fork 才写通道 | `runner/app.py` L3497–3502 `is_fork_launch`；L3740–3747 仅 `external_session_id is None and not is_fork_launch` 传 `developer_instructions` |
| App-server 写 config + receipt | `codex_native_app_server.py` L589–602：先 clear；有 instructions 则 upsert 后 `write_prompt_receipt` |
| 测试 | `test_executor_matching_receipt_allows_rpc`；`test_executor_applied_on_digest_match`；`test_builder_fresh_non_fork_receives_sentinel` |

### Q2. `applied=True` 时，非 strict 是否应当没有 fail-loud warning？

**是（应当没有）。**

| 依据 | 位置 |
|------|------|
| 早返回 apply | `note_native_system_prompt` L79–80：`if applied: return "apply"`（不进入 L82–92 warning 分支） |
| 测试 | `test_executor_applied_on_digest_match`（无 `"not applying"`）；`test_note_applied_skips_warn` |

### Q3. `applied=True` 时，`OMNIGENT_STRICT_PROMPT=1` 是否应当允许继续，而不是失败？

**是（应当允许继续）。**

| 依据 | 位置 |
|------|------|
| applied 先于 strict 检查 | `note_native_system_prompt` L79–80 在 L88–90 的 strict raise 之前返回 |
| 匹配后仍发 RPC | `test_executor_matching_receipt_allows_rpc`：匹配后存在 `turn/start` |
| 测试 | `test_strict_applied_no_error` |

### Q4. resume、fork、receipt 缺失/损坏/不匹配是否分别保持 `applied=False`？

**是（均保持未 apply / fail-loud 路径）。**

| 场景 | 行为 | 依据 |
|------|------|------|
| **resume** | 不传 `developer_instructions`；start 仍 clear receipt → 无匹配 receipt | `app.py` L3740–3747；`test_builder_resume_receives_none`；`test_app_server_start_clears_stale_receipt_without_instructions` |
| **fork（含失败降级）** | `is_fork_launch=True` → instructions=None | `app.py` L3497–3502, L3740–3747；`test_builder_fork_success_receives_none`；`test_builder_fork_fallback_fresh_still_none` |
| **receipt 缺失** | `read` → None → match False | `read_prompt_receipt` L156–157；`receipt_matches_prompt` L174–175；`test_receipt_missing_returns_none`；`test_executor_strict_mismatch_zero_rpc`（无 receipt） |
| **损坏 / 非法 UTF-8** | `read` → None | `read_prompt_receipt` L163–164；`test_receipt_corrupt_returns_none`；`test_invalid_utf8_receipt_returns_none` |
| **不匹配**（错 harness/channel/chars/sha256） | match False | `receipt_matches_prompt` L177–183；`test_receipt_match_rejects_wrong_harness_channel_or_chars` |
| **config upsert 失败** | 不写 receipt | `codex_native_app_server.py` L595–602 时序；`test_app_server_writes_receipt_only_after_config_success` |

### Q5. 其余十个 native harness 是否仍只有 Phase 1 warn/error，没有 apply 通道？

**是。**

| 依据 | 位置 |
|------|------|
| 矩阵仅 codex-native=apply | `native_prompt_delivery.py` L36–48；`test_capability_matrix_only_codex_native_is_apply` |
| 硬编码 `applied=False` | 10 个 executor：`claude_native` L125、`cursor` L89、`goose` L83、`hermes` L84、`kimi` L87、`kiro` L61、`pi` L97、`qwen` L126、`antigravity` L230；`native_server_harness`（opencode）同类 |
| 入口参数化 | `test_native_executor_warns_on_dropped_prompt` / `test_native_executor_strict_errors_before_inject`（11 harness） |
| 阶段 6 | `HERMES_REVIEW_6.md` §3：其余 10 个硬编码 `applied=False`，无伪 apply |

### Q6. 当前 AC-4/AC-5 若绑定到 fresh codex-native，是否与阶段 5 契约冲突？

**是（冲突）。**

| 现行 AC | 现行字面要求 | 与 Phase 2 冲突点 |
|---------|--------------|-------------------|
| **AC-4** | `PRE_MERGE_GATES.md` L306：native 非 strict 须出现 fail-loud **warning**（含 `chars=`） | fresh codex-native + receipt 匹配 → **无** warning（Q2） |
| **AC-5** | L307：strict 须在用户消息注入前**失败** | 匹配时 strict **不失败**（Q3） |
| **启动模板** | L289–294：同一 Executor 流「短消息 → 抓 warning → 再 strict 失败」 | 与 E-positive 同一会话互斥 |

若执行方仍按现行模板用 fresh codex-native 跑 AC-4/5：  
- Phase 2 正确实现 → AC-4/5 字面 **FAIL**（无 warning / 不 fail）→ 错误惩罚正确 apply；或  
- 为通过 AC-4/5 故意破坏 apply → 惩罚正确实现。  
两种结果均使 Gate 2 **无意义**。

**不冲突的部分：** AC-1（workspace 隔离）、AC-2/AC-3（harness/model）、以及 **对无 apply 通道 native 的** AC-4/AC-5 语义。

### Q7. AC-6 是否应改为：只有 receipt、私有 config 快照/摘要、启动日志和真实回复链完整时，才允许声明 codex-native Phase 2 已送达；其他 native 不得声明送达？

**是（应如此收紧；现行 AC-6 方向对但粒度不足）。**

现行 AC-6（L308）：不得写「已送达」——除非另有 Phase2 证据。  
阶段 5/6 已定义 Phase 2 证据形态，但 Gate 2 未列出最小证据清单，易把「无 warning」误读为送达，或把单元测试当实机送达。

**建议 AC-6 判定门槛（实机，非单测）：**

| 证据项 | 要求 |
|--------|------|
| Session | fresh（无 resume/fork 标志）；独立 workspace |
| Receipt | `prompt_delivery.receipt.json` 存在；`harness_id`/`channel`/`chars`/`sha256` 与 agent prompt 一致；**无** prompt 正文 |
| 私有 config | 该 session `codex-home/config.toml` 含顶层 `developer_instructions`；**非**用户共享 `~/.codex/config.toml`（symlink 已 materialize） |
| 日志 | 该轮 **无** `is not applying ... chars=` warning；prompt 正文不出现在 runner/server 日志 |
| 回复链 | 真实模型短回复（如 `EXECUTOR_OK`）；exit 0 |
| 其它 native | **禁止**声称送达，即使无 warning（若 prompt 为空） |

### Q8. 当前 CLI 是否能用非交互 one-shot 创建三个独立 workspace/session，并留下 session id、workspace、harness/model 与日志证据？（静态确认，不启动）

**条件是（静态）：可以；但有关键路径约束。**

| 能力 | 静态依据 | 约束 / preflight |
|------|----------|------------------|
| One-shot 用户消息 | `cli.py` `run`：`-p/--prompt`（L6735）；headless one-shot 设计（L6864–6867, L6526–6528） | 需本地/远程 server + runner；非 TTY 时 bare `run` 行为不同 |
| Agent YAML 路径 | `run [AGENT]` + 可选 `--model` / `--system-prompt` / `--server` | Gate 角色应用**独立 YAML 文件**，非共享 agent id |
| 无 AGENT 的 harness 启动 | `_materialize_harness_launcher_file`（L5959+）生成临时 YAML | 适用于 `claude-sdk` 等 |
| **禁止**用于 E-positive 的路径 | `_dispatch_native_terminal_harness`（L6131+）：`run --harness codex-native` **拒绝** `-p` / `--system-prompt`（L6180–6201），直进 TUI | **E-positive 必须** `run path/to/executor.yaml -p "..."`，走 session+runner+app-server，才能写 private config/receipt |
| Session / workspace 证据 | session 创建后有 conversation id；workspace 来自 session snapshot / `OMNIGENT_RUNNER_WORKSPACE`（`app.py` `_codex_session_workspace`） | 应用**三个不同 workspace 根**或 `isolate_session`；执行前 preflight 记录绝对路径 |
| Bridge / receipt 路径 | `~/.omnigent/codex-native/<sha256(session)[:32]>/`：`prompt_delivery.receipt.json`、`codex-home/config.toml`（`codex_native_bridge.py` L86–96, L267–274） | 证据拷贝时只拷 metadata/摘要，**禁止**把完整 prompt 写入公开报告 |
| Harness/model | YAML `executor.config.harness` / `executor.model`；launch 日志 | pinned model **preflight 实测可选列表**，禁止编造模型名 |

**本机本阶段未验证** CLI 可用性、凭据、端口与真实 exit code → 执行卡须先 preflight；缺 CLI/凭据/第二 native → 对应轮次 **NOT_EXECUTED**（阻塞 merge，写清缺口）。

---

## 4. 最小 Gate 2 实机矩阵（可转写执行卡）

### 4.1 角色与路径总表

| 轮次 | 角色/目的 | 路径 | 必须证明 | 对应 AC（建议修订后） |
|------|-----------|------|----------|----------------------|
| **C** | Controller | 非 native 或已知可用 harness（推荐 `claude-sdk`） | 独立 session/workspace；短回复 token `CONTROLLER_OK` | AC-1（部分） |
| **E-positive** | Executor 正向 Phase 2 | **fresh、非 fork** `codex-native` + 非空 role prompt | AC-2/AC-3；receipt+config 匹配；**无** fail-loud warning；**无** prompt 正文泄漏；真实 `EXECUTOR_OK`；**strict 可继续**（同会话或紧随的 strict 子步，且 receipt 仍匹配） | AC-2, AC-3, AC-4-pos, AC-5-pos, AC-6 |
| **E-neg-warn** | Executor 负向 non-strict | **无 apply 通道** native（首选，见 §4.2） | warning 含 `chars=N`，**无** prompt 正文；用户消息保持原样 | AC-4-neg |
| **E-neg-strict** | Executor 负向 strict | **新**会话，同 harness 能力边界；`OMNIGENT_STRICT_PROMPT=1` | 在任何用户消息 RPC/注入前失败（sole error）；无后续 turn | AC-5-neg |
| **R** | Reviewer | 同 C 类非 native | 独立 session/workspace；`REVIEWER_OK` | AC-1（部分） |

**硬约束：**

- 不得用 resume/fork 冒充 E-positive。  
- 不得用单元测试冒充 Gate 2 smoke。  
- 负向控制**不得**修改用户共享 Codex/Claude 全局配置；仅私有 bridge / 临时 YAML / 隔离 HOME。  
- E-positive 与 E-negative **禁止**共用同一 session id。

### 4.2 负向控制 harness 选择

| 优先级 | 选择 | 依据 | 缺省时 |
|--------|------|------|--------|
| **P0 推荐** | `claude-native`（或矩阵内任一非 codex native，本机 CLI 真实可用者） | `NATIVE_PROMPT_CAPABILITY_MATRIX` 为 `warn`；executor 硬编码 `applied=False`；与 Phase 2 通道无关，语义最干净 | preflight：`claude`/`claude-native` 可启动 |
| **P1 备选** | 其它 warn-only native（`cursor-native` / `pi-native` / …） | 同上，按本机已安装 CLI 选 | 记录实际 harness_id |
| **P2 仅当无第二 native CLI** | **隔离**的 codex-native **receipt-mismatch** 控制：新 session + 人为不匹配（例如 empty instructions 的 YAML 不用于此；更安全：resume 已有 thread **或** 在仅该 session 的 bridge 预置错误 sha256 后**且**不走 fresh apply 写回） | mismatch → `applied=False`（Q4） | **禁止**改 `~/.codex` 共享配置 |
| **禁止** | 用 E-positive 同一 fresh 匹配会话去「期望 warning」 | 与 Q2/Q6 冲突 | — |

**判定建议：**

- 若 P0/P1 本机存在可启动 native CLI → E-neg **必须**跑；失败 = Gate 2 FAIL。  
- 若仅有 codex CLI：允许 P2 receipt-mismatch / resume 负向，但报告必须标明「非第二 harness，而是 mismatch 控制」；证据仍要 `chars=` warning + strict 注入前失败。  
- 若**无任何**可安全制造的负向路径（无第二 native 且不允许碰 bridge）→ E-neg 两轮 **NOT_EXECUTED**，Gate 2 整体 **未完成**（阻塞 merge），**不得**用「E-positive 无 warning」反向证明 Phase 1。

### 4.3 C / R harness 与凭据（只记名，不记值）

| 角色 | 推荐 harness | 备选 | 凭据 / 环境变量名（无值） |
|------|--------------|------|---------------------------|
| C / R | `claude-sdk`（与现行 §2.1 示例一致） | 本机已配置的 `codex`（**非** native TUI）、`openai-agents-sdk` 等非 native | 按本机配置：`ANTHROPIC_API_KEY` / Claude Code login / provider 配置项名；**preflight 只记录「存在/缺失」布尔** |
| E-positive | `codex-native` | 无（Phase 2 唯一 apply 目标） | Codex CLI 登录态 / `OPENAI_API_KEY` 等（名 only）；`codex` 二进制在 PATH |
| E-negative | §4.2 | — | 对应 CLI 凭据存在性 |

**Pinned model：**

1. Preflight 列出该 harness **当前真实可用**模型（CLI/配置查询；本阶段不执行）。  
2. 在 agent YAML 写死 `executor.model: <实测 id>`（非默认占位符）。  
3. 证据：launch 日志 / private `config.toml` 的 `model =` / bridge state 与 YAML **字符串相等** → AC-3。  
4. **禁止**在执行前编造模型名写入报告为「已验证」。

### 4.4 Workspace / 隔离 / 端口 / 清理 / 脱敏

| 项 | 规划（路径示例；执行时改为本机绝对路径） |
|----|------------------------------------------|
| Evidence root | `$EVIDENCE_ROOT` = 例如 `…/gate2-evidence/<RUN_ID>/` |
| C workspace | `$EVIDENCE_ROOT/ws/controller`（空目录 + sentinel 文件 `C_ONLY`） |
| E-pos workspace | `$EVIDENCE_ROOT/ws/executor-pos`（sentinel `E_POS_ONLY`） |
| E-neg workspace | `$EVIDENCE_ROOT/ws/executor-neg`（sentinel `E_NEG_ONLY`；**与 pos 不同**） |
| R workspace | `$EVIDENCE_ROOT/ws/reviewer`（sentinel `R_ONLY`） |
| Agent YAML 目录 | `$EVIDENCE_ROOT/agents/{controller,executor-pos,executor-neg,reviewer}.yaml` |
| HOME 隔离（推荐） | 可选 `OMNIGENT_HOME` / 测试用临时 HOME；**至少**确认 codex private home 在 `~/.omnigent/codex-native/<digest>/codex-home`，不写共享 config |
| 端口 | 本地 server 默认或显式 `--server http://127.0.0.1:<PORT>`；PORT 记入 `env.txt`；避免与残留 host 冲突（**本阶段不清理进程**；执行卡须 preflight 端口空闲） |
| 进程清理边界 | 仅终止**本 RUN_ID** 启动的 server/runner/native 子进程；**禁止** `tmux kill-server` / 无差别 kill；清理清单写入 `cleanup.txt` |
| 日志脱敏 | 拷贝日志前 strip：API key、cookie、完整 `developer_instructions` / `prompt` 正文；保留 `chars=N`、sha256、harness_id、session id、路径 |

**Bridge 证据定位（E-positive，session id = `conv_…`）：**

```text
~/.omnigent/codex-native/<sha256(session_id)[:32]>/
  prompt_delivery.receipt.json    # 仅 metadata
  codex-home/config.toml          # 可证明 developer_instructions 键存在；报告只存 sha256(prompt) 与 chars，不存正文
```

### 4.5 建议角色 YAML 骨架（执行时写入 evidence，不进本仓库源码）

**Controller / Reviewer**（非 native）：

```yaml
name: controller-gate   # reviewer-gate 同理改名与 token
prompt: "You are Controller. Reply with the single token CONTROLLER_OK and stop."
executor:
  harness: claude-sdk
  model: <PINNED_FROM_PREFLIGHT>
```

**Executor positive（codex-native Phase 2）：**

```yaml
name: executor-gate-pos
prompt: "You are Executor. Reply with the single token EXECUTOR_OK and stop."
executor:
  type: omnigent
  config:
    harness: codex-native
    yolo: true
  model: <PINNED_FROM_PREFLIGHT>
```

说明：`prompt:` 经 `omnigent.spec.omnigent` 译为 `AgentSpec.instructions`（`instructions:` 优先于 `prompt:`），再经 `_codex_native_developer_instructions` 进入 private `developer_instructions`。

**Executor negative（例：claude-native）：**

```yaml
name: executor-gate-neg
prompt: "You are Executor-Neg. Reply with EXECUTOR_NEG_OK and stop."
executor:
  type: omnigent
  config:
    harness: claude-native
  model: <PINNED_FROM_PREFLIGHT_OR_OMIT>
```

### 4.6 命令模板、预期退出码、证据文件、超时

> 以下为**后续执行卡**模板。本阶段**不得**运行。`<CLI>` = `omnigent-zh` 或 `uv run omnigent`（preflight 二选一记录实际路径）。

#### Preflight（exit 0 才继续）

| 步骤 | 命令意图 | 证据 | 失败 → |
|------|----------|------|--------|
| P1 | `<CLI> --version` | `version.txt` | NOT_EXECUTED |
| P2 | 检查 codex / claude 等 CLI 在 PATH | `cli-which.txt` | 缺 codex → E-pos NOT_EXECUTED；缺 neg CLI → 按 §4.2 |
| P3 | 凭据存在性（名 only） | `creds-presence.txt`（true/false） | 缺 → 对应轮 NOT_EXECUTED |
| P4 | 端口空闲 + 无冲突 host | `ports.txt` | 改 PORT 或中止 |
| P5 | 解析/记录 pinned model | `models-preflight.txt` | 无可用模型 → NOT_EXECUTED |
| P6 | 创建四 workspace + sentinel | `ws-layout.txt` | — |

#### 轮次命令（模板）

| 轮次 | 命令模板 | 环境 | 预期 exit | 超时（建议） | 证据文件 |
|------|----------|------|-----------|--------------|----------|
| **C** | `<CLI> run "$EVIDENCE_ROOT/agents/controller.yaml" -p "ping" --model <PINNED> 2>&1 \| tee c-smoke.log` | 无 STRICT；`cwd` 或 runner workspace = C ws | **0**；stdout 含 `CONTROLLER_OK` | 180s | `c-smoke.log`, `sessions.txt` 追加 session/workspace |
| **E-pos** | `<CLI> run "$EVIDENCE_ROOT/agents/executor-pos.yaml" -p "ping" --model <PINNED> 2>&1 \| tee e-pos-smoke.log` | **unset** `OMNIGENT_STRICT_PROMPT` 先跑；可选第二命令同 session **或** 新 turn 设 `OMNIGENT_STRICT_PROMPT=1` 证明仍继续 | **0**；`EXECUTOR_OK`；日志**无** `is not applying`；receipt 匹配；config 有 `developer_instructions` 键 | 300s | `e-pos-smoke.log`, `e-pos-receipt.json`（拷贝）, `e-pos-config-summary.txt`（仅键/chars/sha256）, `e-pos-harness-model.txt` |
| **E-neg-warn** | `<CLI> run "$EVIDENCE_ROOT/agents/executor-neg.yaml" -p "ping" 2>&1 \| tee e-neg-warn.log` | **unset** STRICT | 会话可完成或带 warning 仍 exit 0（以产品为准）；**必须**日志含 `not applying` 与 `chars=`；**无** prompt 正文 | 300s | `e-neg-warn.log` |
| **E-neg-strict** | `$env:OMNIGENT_STRICT_PROMPT='1'; <CLI> run ...executor-neg.yaml -p "ping" ...` | **STRICT=1**；**新** session | **非 0** 或会话错误事件；注入前失败；无成功模型回复依赖 | 180s | `e-neg-strict.log`（时间序证明失败在 inject 前） |
| **R** | 同 C，换 reviewer YAML / token | 无 STRICT | **0** + `REVIEWER_OK` | 180s | `r-smoke.log`, `sessions.txt` |

**E-pos strict 子步说明：**  
在 receipt 仍匹配的前提下设置 `OMNIGENT_STRICT_PROMPT=1` 再发一条短消息，预期 **继续成功**（证明 AC-5-pos）。**不可**用该成功去替代 E-neg-strict。

#### `sessions.txt` 最低字段

```text
role=C|E-pos|E-neg-warn|E-neg-strict|R
session_id=...
workspace_abs=...
harness=...
model=...
strict=0|1
exit_code=...
log=...
```

#### AC 通过条件（修订后语义）

| ID | 通过条件 |
|----|----------|
| AC-1 | C / E-pos / R（及 E-neg）workspace 路径互异；sentinel 文件不串 |
| AC-2 | E-pos launch/harness_kind = `codex-native` |
| AC-3 | E-pos 实际 model = YAML pin |
| AC-4-pos | E-pos 日志**无** fail-loud `not applying`（在非空 prompt + 匹配 receipt 下） |
| AC-4-neg | E-neg-warn 有 `chars=N` warning，无正文 |
| AC-5-pos | E-pos + STRICT 仍可完成 turn（匹配 receipt） |
| AC-5-neg | E-neg-strict 注入前失败 |
| AC-6 | 仅当 E-pos 证据链完整时，报告可写「codex-native Phase 2 已送达」；其它 native 禁止 |

任一必跑轮次 FAIL → Gate 2 **FAIL**。  
必跑轮次因环境 NOT_EXECUTED → Gate 2 **未完成**（阻塞 merge）。

---

## 5. `PRE_MERGE_GATES.md` §2 最小逐字修订建议

**本轮未修改该文件。** 仅建议 Codex/用户批准后另卡落地。

### 5.1 替换 §2.2 启动步骤（建议全文）

```markdown
### 2.2 启动步骤（模板）

```bash
# 使用已安装的 zh-cn CLI（或 uv run）
omnigent-zh --version | tee "$EVIDENCE_ROOT/agentcenter/version.txt"

# 0) preflight：CLI / 凭据存在性（只记名）/ 可用 model 列表 / 端口 / 四 workspace
# 1) C、E-pos、E-neg、R 使用独立 agent YAML 与互不共享的 workspace
# 2) 记录 session id 与 workspace 绝对路径到 agentcenter/sessions.txt
# 3) C / R：非 native harness one-shot 短消息，记录 token 回复
# 4) E-positive：fresh 非 fork codex-native；证明 harness/model、receipt+私有 config、
#    无 fail-loud warning、真实回复；可选 STRICT=1 且 receipt 匹配时仍继续
# 5) E-negative non-strict：无 apply 通道 native（或隔离 receipt-mismatch）→ warning chars=N
# 6) E-negative strict：新会话 + OMNIGENT_STRICT_PROMPT=1 → 用户消息注入前失败
# 7) 禁止用 resume/fork 冒充 E-positive；禁止单元测试替代本 smoke
```

具体 CLI 以当前 `omnigent-zh` / Web UI 为准；**缺 CLI 或角色文件则 Gate 2 = 未执行**，不得编造。
```

### 5.2 替换 §2.3 断言表（建议）

| ID | 断言 | 证据 |
|----|------|------|
| AC-1 | Controller / Executor(s) / Reviewer **workspace 互不共享** | `sessions.txt` + 各 workspace 列表 |
| AC-2 | E-positive：**声明的 `codex-native` 未被换成其它 harness** | launch 日志 / harness_kind |
| AC-3 | E-positive：**实际 model = YAML pin** | launch 日志 / private config model |
| AC-4-pos | E-positive（fresh 匹配 receipt）：**不得**出现 fail-loud `not applying` warning | `e-pos-smoke.log` |
| AC-4-neg | E-negative non-strict：**必须**出现 fail-loud warning（`chars=`，**无** prompt 正文） | `e-neg-warn.log` |
| AC-5-pos | E-positive + `OMNIGENT_STRICT_PROMPT=1` 且 receipt 匹配：**允许继续**（非失败） | `e-pos-strict.log` 时间序 |
| AC-5-neg | E-negative + strict：**在用户消息注入 native 前失败** | `e-neg-strict.log` 时间序 |
| AC-6 | **仅当** receipt + 私有 config 摘要 + 启动日志 + 真实回复链完整时，可声明 **codex-native Phase 2 已送达**；**任何其它 native 不得**声明送达；禁止把 fail-loud 或单测写成送达 | 审查文案 + E-pos 证据包 |

> 兼容说明：若短期需保留 AC-4/AC-5 旧编号，则必须在正文中写明「AC-4/AC-5 **仅**适用于 E-negative；E-positive 适用 AC-4-pos/AC-5-pos」，禁止再写「native 一律 warning/strict fail」。

### 5.3 §2.1 环境变量注释建议

将：

```bash
# 非 strict 跑一轮 native 后，再：
export OMNIGENT_STRICT_PROMPT=1   # 仅用于 strict 断言轮次
```

改为：

```bash
# E-negative strict 轮次专用（新会话）：
export OMNIGENT_STRICT_PROMPT=1
# E-positive 验证「匹配 receipt 时 strict 仍继续」时也可设置，但不得与 E-negative 共用 session
```

### 5.4 不建议改动的部分

- AC-1 / AC-2 / AC-3 的隔离与 harness/model 精神。  
- 「缺 CLI → 未执行、阻塞 merge」的失败安全。  
- Gate 1 相对 PASS ≠ 全仓 GREEN ≠ Gate 2 ≠ merge 的全局政策。

---

## 6. 与现行政策/实现的对照清单

| 项 | 冲突? | 处理 |
|----|-------|------|
| AC-4 绑 fresh codex-native | **是** | 拆 AC-4-pos / AC-4-neg |
| AC-5 绑 fresh codex-native | **是** | 拆 AC-5-pos / AC-5-neg |
| AC-2 / AC-3 | 否 | 保留在 E-pos |
| AC-6 | 部分过宽 | 收紧证据清单（§3 Q7） |
| §2.2 步骤 4–5 单会话流 | **是** | 按 §5.1 分轨 |
| 阶段 5 代码 + 阶段 6 approve | 否（内部自洽） | Gate 2 应验证该契约，而非惩罚它 |
| Gate 1 相对 PASS | n/a | 不开放 merge；不代替 Gate 2 |

---

## 7. 后续执行卡应包含的显式 preflight 未知项

执行前**不得编造**，必须实测写入证据：

1. 本机 `<CLI>` 实际可执行路径与版本。  
2. `codex` / 负向 native CLI 是否在 PATH。  
3. 凭据环境变量**是否存在**（不写值）。  
4. 可选模型列表与最终 pin。  
5. 本地 server 端口与是否已有残留 daemon（处理策略：只登记，清理边界见 §4.4）。  
6. Windows vs Linux 证据机：Gate 2 是否要求与 Gate 1 同机；若跨 OS，路径与 HOME 规则写死。  
7. `omnigent run <yaml> -p` 对 `codex-native` agent 是否在本环境走出 runner/app-server 路径（静态期望：是；实机以 bridge 目录出现 receipt 为准）。

---

## 8. 禁止项遵守声明

本阶段：

- 未运行 pytest、Ruff、Gate 1/2、omnigent-zh 实机 smoke、任何真实模型 CLI。  
- 未启动/终止 host/server/tmux。  
- 未修改 `PRE_MERGE_GATES.md`、源码、tests、STATUS、POST_FIX、旧 handoff。  
- 未读取/打印 credentials、token、真实用户 HOME 私密内容或 prompt 正文。  
- 未将 Gate 1 相对 PASS 写成全仓 GREEN。  
- 未宣称 Gate 2 PASS 或可 merge。  
- 未 stage/commit/push/merge/tag。  
- 工作树本阶段**仅新增**本文件 `docs/fixes/handoffs/GROK_GATE2_POLICY_REVIEW.md`。

---

## 9. 交回 Codex

| 项 | 内容 |
|----|------|
| 冲突结论 | **AC-4/AC-5 绑 fresh codex-native 与 Phase 2 正向 apply 冲突（确定）** |
| 矩阵 | C / E-pos / E-neg-warn / E-neg-strict / R 已给出 |
| 政策 | 仅建议修订文案；**待批准后另卡**修改 `PRE_MERGE_GATES.md` |
| Gate 1 | PASS（相对 main）；**非**全仓 GREEN |
| Gate 2 | **仍未执行、未判定** |
| Merge | **不可 merge** |

**停止。** 等待 Codex 只读验收。不得自行改政策或执行 Gate 2。
