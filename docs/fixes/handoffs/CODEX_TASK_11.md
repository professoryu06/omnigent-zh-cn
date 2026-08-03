# CODEX TASK 11 — 阶段 10 Windows workspace 契约独立静态审查

> **执行者：** Grok（独立审查者；未参与阶段 10实现）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **审查方式：** 只读静态审查；不得运行 pytest、Ruff、Gate 或真实 CLI。  
> **唯一仓库交付：** `docs/fixes/handoffs/GROK_REVIEW_11.md`

**目标：** 独立判断阶段 10 Windows workspace 绝对路径修复的代码、测试、范围与证据表述是否足以进入全新 Gate 2 重跑策划。

**当前状态：** HEAD=`dc83140c73ceb12fa165753c1880c19f68da86f4`；Gate 1=`PASS（相对 main）`、非全仓 GREEN；Gate 2=`FAIL`、尚未重跑；不可 merge。

---

## 1. 必读材料

必须完整读取：

1. `docs/fixes/handoffs/CODEX_TASK_10.md`
2. `docs/fixes/handoffs/HERMES_COMPLETION_10.md`，特别是“返工轮次”
3. `docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_2.md`
4. `docs/fixes/PRE_MERGE_GATES.md` §2
5. `omnigent/server/routes/_workspace_validation.py`
6. `omnigent/server/routes/sessions.py` 中 `_validate_session_workspace()`
7. `tests/server/routes/test_workspace_validation.py`
8. `tests/server/routes/test_workspace_validation_helpers.py`

阶段 10开始前固定 blob：

| 文件 | 开始前 blob |
|---|---|
| `omnigent/server/routes/_workspace_validation.py` | `7401b7422644f2fb38a57cd8a492194a6bfb8cd0` |
| `omnigent/server/routes/sessions.py` | `fb77bc23147828eec70a1c50765dd5c754503241` |
| `tests/server/routes/test_workspace_validation.py` | `c23001c441cb22130d09e4d6cd97151ee5d22824` |
| `tests/server/routes/test_workspace_validation_helpers.py` | `1820f67f6a6143900db65ec1015e332bff7be37a` |

保护值：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- workspace blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve blob：`6116218097f2352c467524fd0ddf0838315aa524`

## 2. 审查边界与允许操作

只允许读取文件以及运行以下只读命令：

```powershell
git status --short --branch
git rev-parse HEAD
git diff --name-only
git diff -- omnigent/server/routes/_workspace_validation.py omnigent/server/routes/sessions.py tests/server/routes/test_workspace_validation.py tests/server/routes/test_workspace_validation_helpers.py
git hash-object tests/runner/test_session_workspace_cache.py
git hash-object tests/runner/test_app_codex_native_model.py
git hash-object tests/runner/test_runner_idle_active_work.py
git hash-object tests/runner/transports/ws_tunnel/test_serve.py
```

可使用 `rg`、`Get-Content` 等只读文本检查。不得运行：

- pytest、Ruff、mypy、全仓测试或覆盖率；
- Gate 1、Gate 2、server、host、runner、真实 CLI smoke；
- 任何会修改源码、tests、policy、STATUS、旧 handoff 或 evidence 的命令。

如果静态审查认为必须补测，只能在报告中写出精确测试文件、测试名、命令与预期；交 Codex另发 Hermes返工卡。Grok不得自行新增测试或修改实现。

## 3. 精确静态审查清单

### 3.1 absolute-path 分类

检查 `_is_absolute_path(path: str) -> bool` 是否满足：

- POSIX `/...` 接受；
- Windows drive-absolute `C:\...` 与 `C:/...` 接受；
- 完整 UNC `\\server\share` 接受；
- `some/relative`、`~/projects`、`C:relative`、`\rooted-without-drive`拒绝；
- 不以冒号、反斜杠存在性或 server当前 OS作为判断依据；
- 不调用 `Path.resolve()`、`os.path.abspath()` 或 server本地文件系统解释 remote host路径。

重点检查正则或等价纯语法判断是否会把明显不完整 UNC、drive-relative 或仅根相对路径误放。

### 3.2 两层入口统一

确认：

- `validate_workspace()` 与 `_validate_session_workspace()` 调用同一个 absolute-path helper；
- route层仍保持 `workspace is None`、agent cache、host registry和ownership检查次序；
- Windows路径不会在 route层提前 400；
- 错误消息没有泄露路径之外的敏感信息。

审查新增 `test_validate_session_workspace_accepts_windows_drive_absolute_path` 是否真的直接调用 `_validate_session_workspace()` 并跨过其重复 guard。特别核对测试中的 raw string是否使用了符合正式 Gate路径形状的单分隔符 `C:\Users\...`；若双重分隔符会弱化回归价值，按严重度列出。

### 3.3 canonical boundary安全性

检查 `_is_subpath_of()`：

- POSIX继续大小写敏感；
- Windows按大小写不敏感和 `\`/`/`等价语义比较；
- 同一路径、子目录、root boundary正确；
- prefix collision拒绝；
- Windows不同 drive拒绝；
- POSIX/Windows混合 flavor拒绝；
- 比较仅针对 host已返回的 canonical paths，未绕过既有 symlink canonicalization。

额外检查 UNC boundary、share边界以及尾随分隔符是否存在误包含或误拒绝风险。若现有测试不足以判定，列为明确补测项，不得凭推测 approve。

### 3.4 `./subdir`拼接

确认：

- Windows drive与UNC canonical workspace使用 host可识别的 Windows分隔符；
- POSIX保持 `/`；
- 不转换成 `/mnt/c/...`、不做 WSL映射；
- 输入 workspace仍原样发给 `host.stat`，最终只存 host返回的 canonical path；
- 原有 subdir存在性与 symlink防护语义未被移除。

### 3.5 测试充分性

逐项映射测试与契约：

| 契约 | 必须找到的覆盖 |
|---|---|
| Windows drive absolute | validator正向 |
| route重复 guard | `_validate_session_workspace()`直接用例 |
| drive-relative/root-relative | 两个负向用例 |
| Windows boundary | same/child/case/prefix/different drive/not-child |
| UNC | absolute、boundary、subdir三条 |
| POSIX回归 | 原有 absolute/boundary/subdir/symlink/relative/tilde测试仍在 |

不得把“测试代码存在”写成“Grok独立运行通过”。本轮不跑测。

### 3.6 范围与最小性

核对阶段 10只触及：

1. `omnigent/server/routes/_workspace_validation.py`
2. `omnigent/server/routes/sessions.py`
3. `tests/server/routes/test_workspace_validation.py`
4. `tests/server/routes/test_workspace_validation_helpers.py`
5. `docs/fixes/handoffs/HERMES_COMPLETION_10.md`

工作树中其它既有改动属于阶段 1/3/5、Gate政策和 r05，不得误判为阶段 10越权，也不得清理。

检查是否存在不必要的 protocol/schema/database/frontend/dependency/CI变化；存在即至少 P1。

## 4. 证据债务必须单独判定

Codex只读验收已将阶段 10标记为 `ACCEPT_WITH_EVIDENCE_DEBT`。Grok必须保持以下事实，不得改写：

1. 原始 RED记录了五个失败 nodeid与关键错误，但没有可信的真实退出码；不得称为完整可审计 RED退出码链。
2. Hermes返工报告记录的定向 `9 passed`、全套 `43 passed`、影响套件 `29 passed`、保护 `17 passed`、Ruff clean和diff-check exit 0均是 Hermes结果，不是 Grok独立结果。
3. `tests/host/test_connect.py -k "stat"` 是 `1 failed / 6 passed`，不是 GREEN；报告同时写 `exit 0`，该退出码不可信。
4. 失败 nodeid `test_handle_stat_expands_tilde` 已在 `HERMES_COMPLETION_3.md`记录为既有 Windows tilde问题；本阶段未修改其生产/测试文件，因此可作为阶段 10外部剩余风险，但不得写成“全部影响测试通过”。

审查报告必须判断：这些证据债务是否阻止进入全新 Gate 2策划。即使判断不阻止，也必须保留为 P2/剩余风险，不能删除或改成 GREEN。

## 5. 严重度与结论规则

问题分级：

- **P0：** 路径校验造成明显任意边界逃逸、敏感信息泄漏或破坏已有安全不变量。
- **P1：** 正式 Windows Gate路径仍会被拒绝、相对路径被误放、route层未真正覆盖、Windows/UNC boundary错误、跨阶段修改，或必须补代码/测试后才能重跑 Gate 2。
- **P2：** 不阻断功能的测试表达、注释、证据债务或剩余平台风险。

最终结论只能是：

- `approve`：P0/P1均无；允许 Codex编写全新 Gate 2重跑任务卡。不是 Gate 2 PASS，不批准 merge。
- `request-changes`：存在任一 P0/P1；列出精确必须修改项，退回 Codex决定 Hermes返工。

不要使用“看起来通过”“基本 approve”或“可 merge”等模糊结论。

## 6. 唯一输出

只新建：

`docs/fixes/handoffs/GROK_REVIEW_11.md`

必须包含：

1. 唯一结论：`approve`或`request-changes`。
2. P0/P1/P2逐级列表；无则明确写“无”。
3. absolute分类、两层入口、boundary、subdir和测试映射逐项结论。
4. 阶段 10文件范围与HEAD/四保护blob核对。
5. 明确说明本轮未运行任何测试、Ruff、Gate或真实CLI。
6. 原始 RED退出码缺失、host stat非GREEN/退出码不可信的证据评级。
7. 必须修改项与剩余风险。
8. 是否允许 Codex进入“全新 Gate 2 RUN任务卡策划”。
9. 明确：Gate 1仍为相对 main PASS、非全仓 GREEN；Gate 2仍为FAIL、未重跑；不可 merge。
10. 最终 `git status --short --branch`，并声明除本报告外未修改仓库文件。

## 7. 禁止项

- 不得修改源码、tests、fixture、依赖、lockfile、CI、policy、STATUS、POST_FIX或任何旧handoff。
- 不得修改、补写或清理 Gate evidence。
- 不得运行 pytest、Ruff、Gate 1、Gate 2、server/host/runner或真实CLI smoke。
- 不得自行修复发现的问题；只能报告并交回 Codex。
- 不得把 Hermes测试数字冒充 Grok独立运行。
- 不得把既有 host stat失败标为 GREEN。
- 不得用单测、receipt-mismatch、resume、fork或旧evidence代替未来真实Gate 2轮次。
- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得 commit/push/merge/tag、发版或编辑PR/Issue。
- 不得把 `approve`写成 Gate 2 PASS或可 merge。

## 8. 完成标准

阶段 11只有在以下全部满足时完成：

1. Grok未修改被审代码、测试、旧文档或evidence，只新建 `GROK_REVIEW_11.md`。
2. 已逐行审查阶段 10实际 diff，而非复述 Hermes摘要。
3. 已逐项判断路径分类、route层、Windows/UNC boundary、subdir和安全不变量。
4. 已核对测试存在性与断言强度，但未运行测试。
5. 已诚实保留两项证据债务与host stat非GREEN事实。
6. P0/P1/P2、必须修改项和剩余风险完整。
7. HEAD与四保护blob匹配；无commit/push/merge/tag。
8. 结论没有改变 Gate状态或授权merge。

完成后停止，交回 Codex只读验收。若 `approve`，Codex下一阶段只可策划全新 Gate 2 RUN；若 `request-changes`，由Codex另发Hermes返工卡。
