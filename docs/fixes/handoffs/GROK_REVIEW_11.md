# GROK REVIEW 11 — 阶段 10 Windows workspace 契约独立静态审查

**审查者：** Grok（独立审查者；未参与阶段 10 实现）  
**日期：** 2026-07-30  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_11.md`  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**审查方式：** 只读静态审查；**未**运行 pytest / Ruff / Gate / server / host / runner / 真实 CLI。

---

## 1. 唯一结论

### **`approve`**

- **P0：无**  
- **P1：无**  
- **P2：有**（证据债务、route 测试路径字面量双反斜杠、host stat 非 GREEN、少量补测建议）

**含义：** 允许 Codex **策划全新 Gate 2 RUN 任务卡**。  
**不**表示 Gate 2 PASS。  
**不**批准 merge。  
**不**表示全仓 GREEN。

Gate 1 仍为 **PASS（相对 main）**，非全仓 GREEN。  
Gate 2 仍为 **FAIL（0202 RUN）**，**尚未**因本修复重跑。  
**不可 merge。**

---

## 2. P0 / P1 / P2

### P0

**无。**

未发现任意路径边界逃逸、敏感信息泄漏（超出既有 path 插值错误文案）或破坏 symlink-canonical 不变量的实现缺陷。

### P1

**无。**

正式 Gate 2 形态的 Windows drive-absolute（`C:\...` 单分隔符）在纯语法层由 `_is_absolute_path` 接受；两层入口均改用该 helper；boundary / subdir 对 Windows/UNC 有明确逻辑与测试映射。无必须先改代码才能策划重跑 Gate 2 的阻塞项。

### P2

1. **原始 RED 退出码缺失（证据债务）**  
   Hermes 记录了失败 nodeid 与关键错误，但无可信的真实进程退出码链；不得称为完整可审计 RED exit 链。

2. **Hermes GREEN 数字非本审查独立复验**  
   定向 `9 passed`、全套 `43 passed`、影响 `29 passed`、保护 `17 passed`、Ruff clean、diff-check 0 均为 Hermes 报告，**不是** Grok 运行结果。本轮不冒充。

3. **host stat 套件非 GREEN**  
   Hermes：`tests/host/test_connect.py -k "stat"` → **1 failed / 6 passed**，且报告写 exit 0 → **退出码不可信**。失败 nodeid `test_handle_stat_expands_tilde` 与阶段 3 既有 Windows tilde 问题一致；阶段 10 未改 host/connect 生产或该测试文件。保留为**阶段 10 外部剩余风险**，不得写成“影响测试全绿”。

4. **route 层回归用例路径字面量**  
   `test_validate_session_workspace_accepts_windows_drive_absolute_path` 使用  
   `workspace=r"C:\\Users\\runner\\project"`  
   在 Python 中求值为 **双反斜杠** 形态（`C:\\Users\\...`），而非 Gate 2 实机常见的 **单分隔符** `C:\Users\...`。  
   语法上仍满足 drive-absolute，**不阻止**生产接受 Gate 路径；但**弱化**对正式 Gate 路径形状的回归价值。建议后续（非本轮）改为 `r"C:\Users\runner\project"` 单分隔符。

5. **补测建议（非阻断）**  
   - `_is_subpath_of` 对 mixed flavor（POSIX vs Windows）的显式 unit 用例；  
   - UNC share 级 prefix-collision（如 `\\s\share2` vs `\\s\share`）在 helpers 层的显式用例（当前经 validate_workspace UNC 间接覆盖 child/same）。

---

## 3. 清单逐项结论

### 3.1 absolute-path 分类 — **通过**

实现：`omnigent/server/routes/_workspace_validation.py` 中 `_is_absolute_path`（L54–75）+ 正则 L48–51。

| 形状 | 静态结论 |
|------|----------|
| POSIX `/...` | `startswith("/")` → 接受 |
| Windows `C:\...` / `C:/...` | `_WIN_DRIVE_ABSOLUTE_RE` `^[A-Za-z]:[\\/]` → 接受 |
| UNC `\\server\share` / `//server/share` | `_WIN_UNC_ABSOLUTE_RE` 要求 server+share 两段 → 接受完整 UNC |
| `some/relative`、`~/projects`、`C:relative`、`\rooted-without-drive` | 不匹配上述规则 → 拒绝 |
| 不完整 UNC（如仅 `\\server`） | share 段缺失 → 拒绝（静态推演） |

**未**使用 `Path.resolve()` / `os.path.abspath()` / server 本机 FS 解释 remote 路径。  
**未**以“含冒号/含反斜杠”单独判绝对。

### 3.2 两层入口统一 — **通过**

| 入口 | 判定 |
|------|------|
| `validate_workspace()` L279 | `_is_absolute_path(workspace)` |
| `_validate_session_workspace()` sessions.py L6182 | 同一 `_is_absolute_path` |
| 次序 | None → absolute → agent_cache → host_registry → **ownership（host_store 时）** → load spec → `validate_workspace` |
| Windows 提前 400 | 旧 `startswith("/")` 已移除；drive-absolute 不再在 route 层被挡 |
| 错误文案 | 改为 `POSIX /... or Windows C:\...`；仍含用户 path 的既有模式未扩大敏感面 |

**Route 测试：**  
`test_validate_session_workspace_accepts_windows_drive_absolute_path` **直接**调用 `_validate_session_workspace`，monkeypatch 共享 `validate_workspace`，断言 workspace 被传入且非 OmnigentError 400。  
**P2：** 字面量双反斜杠（见上）。

### 3.3 canonical boundary — **通过（带 P2 补测建议）**

`_is_subpath_of` L196–240：

- 混合 flavor → False  
- Windows：`/`→`\`、lower、sep=`\`；POSIX：原样、sep=`/`  
- 等路径 / 子目录 / trailing sep / prefix collision 逻辑保留  
- 输入声明为 host.stat 的 canonical realpath，**未**绕过 symlink canonicalization  

Helpers 有 Windows same/child/case/prefix/drive/not-child 六测；UNC boundary 在 validate 层有用例。  
无 P1 级 boundary 逃逸静态发现。

### 3.4 `./subdir` 拼接 — **通过**

L360–365：Windows flavor 用 `\` 拼接，POSIX 用 `/`；**无** `/mnt/c` / WSL 映射。  
输入 workspace 仍以原样 `path=workspace` 发给 `_ask_host_stat`；返回值仅为 host `canonical_path`。  
subdir 存在性检查保留。

### 3.5 测试映射（存在性；**未运行**）

| 契约 | 覆盖位置（静态） |
|------|------------------|
| Windows drive absolute | `test_windows_drive_absolute_workspace_accepted` |
| route 重复 guard | `test_validate_session_workspace_accepts_windows_drive_absolute_path` |
| drive-relative / root-relative | `test_windows_drive_relative_rejected`、`test_windows_rooted_without_drive_rejected` |
| Windows boundary helper | same/child/case/prefix/different drive/not-child |
| Windows boundary via validate | `test_windows_boundary_accepted` |
| Windows subdir | `test_windows_subdir_accepted` |
| UNC absolute/boundary/subdir | `test_unc_absolute_workspace_accepted` 等 3 条 |
| POSIX 回归 | 原有 offline/exist/dir/boundary/symlink/subdir/relative/tilde 等仍在文件中 |

**不得**将“测试存在”写成“Grok 独立跑通”。

### 3.6 范围与最小性 — **通过**

阶段 10 触达（相对 HEAD 的相关 diff / 新建）：

1. `omnigent/server/routes/_workspace_validation.py`（blob 已变，符合预期）  
2. `omnigent/server/routes/sessions.py`（仅 absolute 判断 + import/消息）  
3. `tests/server/routes/test_workspace_validation.py`  
4. `tests/server/routes/test_workspace_validation_helpers.py`  
5. `docs/fixes/handoffs/HERMES_COMPLETION_10.md`（新建）  

工作树其它 M/?? 属阶段 1/3/5、Gate 政策、r05 等**既有**累积，**不**计为阶段 10 越权，本审查不清理。  
**无** protocol/schema/DB/frontend/dependency/CI 变更归因于阶段 10。

---

## 4. 身份与保护 blob

| 项 | 期望 | 本轮核对 |
|----|------|----------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` | 匹配 |
| workspace 测试 | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | 匹配 |
| model 测试 | `be43ec45816e8ece4192822506df8072580910e0` | 匹配 |
| idle 测试 | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | 匹配 |
| serve 测试 | `6116218097f2352c467524fd0ddf0838315aa524` | 匹配 |

阶段 10 目标文件当前 hash（相对“开始前 blob”已变化，属预期修改）：

| 文件 | 开始前 blob（任务卡） | 当前（只读 hash-object） |
|------|----------------------|---------------------------|
| `_workspace_validation.py` | `7401b742…` | `5bf5e587…`（已改） |
| `sessions.py` | `fb77bc23…` | `0375e5f9…`（已改） |
| `test_workspace_validation.py` | `c23001c4…` | `63291bfa…`（已改） |
| `test_workspace_validation_helpers.py` | `1820f67f…` | `4cae0f53…`（已改） |

---

## 5. 证据债务是否阻止全新 Gate 2 策划

| 债务 | 阻止策划？ |
|------|------------|
| RED 无真实 exit 码 | **否**（P2）；nodeid/错误语义已钉死 `startswith("/")` 根因，与 0202 Gate 实机 400 一致 |
| Hermes 数字非独立复验 | **否**（P2）；静态代码与 Gate 失败形态对齐足以策划重跑 |
| host stat 1 fail + 不可信 exit 0 | **否**（P2 外部风险）；非本 diff 引入，不标 GREEN |

**结论：** 证据债务**不阻止** Codex 进入「全新 Gate 2 RUN 任务卡策划」；必须在策划卡中保留债务与 host tilde 风险说明。

---

## 6. 必须修改项与剩余风险

### 必须修改项（approve 条件下）

**无。** 无 P0/P1 强制返工项。

### 剩余风险 / 建议（P2）

1. Gate 2 实机仍可能因 host daemon / runner / 路径存在性等**非本契约**问题失败。  
2. host tilde expand 在 Windows 上仍失败（既有）。  
3. route 测试改为单分隔符路径字面量（建议，非强制）。  
4. 定向/保护测试建议由执行卡在 RED/GREEN 流程中由开发者复跑；审查方未跑。

---

## 7. 是否允许 Codex 策划全新 Gate 2 RUN

**是 — 允许。**

条件与边界：

- 新 RUN_ID、不拼接 0130/0134/0136/0159/0202 证据；  
- 继续 REWORK 2 拓扑：UTF-8、前台 host online、单驱动、清理完整、leak-scan 最后；  
- **不得**因本 `approve` 宣称 Gate 2 PASS 或可 merge。

---

## 8. 本轮未执行声明

未运行：pytest、Ruff、mypy、Gate 1/2、server、host、runner、真实 CLI smoke、任何修改性命令。  
未修改源码、tests、政策、STATUS、旧 handoff、evidence。  
**仅新建**本文件 `docs/fixes/handoffs/GROK_REVIEW_11.md`。

---

## 9. 最终 git status（声明）

审查结束时工作树仍为大量既有 M/??（阶段累积 + 阶段 10 四文件 + handoff 目录）。  
**本审查新增：** `docs/fixes/handoffs/GROK_REVIEW_11.md`。  
**未** stage/commit/push/merge/tag。

代表性身份（只读）：

```text
HEAD=dc83140c73ceb12fa165753c1880c19f68da86f4
branch=docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
四保护 blob：均匹配期望
```

---

## 10. 交回 Codex

| 项 | 值 |
|----|-----|
| 结论 | **`approve`** |
| Gate 2 策划 | **允许**编写全新 RUN 任务卡 |
| Gate 1 | PASS（相对 main）；非全仓 GREEN |
| Gate 2 | 仍 FAIL（旧 RUN）；**未**因阶段 10 重跑 |
| Merge | **不可 merge** |

**停止。** 等待 Codex 只读验收本审查报告。
