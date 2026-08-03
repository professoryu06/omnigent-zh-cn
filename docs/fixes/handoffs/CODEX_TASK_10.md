# CODEX TASK 10 — Windows workspace 绝对路径契约修复

> **执行者：** Hermes（开发者）  
> **方法：** 严格 RED → 最小修复 → GREEN；一次只做本阶段。  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**目标：** 修复 Gate 2 正式 RUN 在 Windows host 上把合法的 `C:\...` workspace 误判为“必须以 `/` 开头”的问题，同时保持 POSIX、相对路径、边界和 symlink 防逃逸语义。

**实现边界：** server 不应使用自身操作系统解释 host 路径；路径语法按纯路径类型判断，存在性和 canonical path 仍只信任目标 host 的 `host.stat`。本阶段不执行 Gate 2，也不宣称修复后可 merge。

**当前状态：** HEAD=`dc83140c73ceb12fa165753c1880c19f68da86f4`；Gate 1=`PASS（相对 main）`、非全仓 GREEN；Gate 2=`FAIL`；不可 merge。

---

## 1. 问题与证据

唯一结论 RUN：

`C:\Users\Administrator\gate2-evidence\20260730-0202-dc83140-grok-gate2-r2\`

已由 Codex 验收为 `ACCEPT_FAIL`。该 RUN 中 server、foreground host、exit 与清理均可信，C 在创建 runner 时收到 400：

```text
Failed to launch a runner ... (400):
workspace must be an absolute path starting with /
```

实际 workspace 是 Windows host 上的合法 drive-absolute 路径 `C:\...`。当前存在两层 POSIX-only 拒绝：

1. `omnigent/server/routes/sessions.py::_validate_session_workspace()` 使用 `workspace.startswith("/")`。
2. `omnigent/server/routes/_workspace_validation.py::validate_workspace()` 使用同样判断。

此外，`_is_subpath_of()` 和 `./subdir` 拼接只按 `/` 工作。若仅删除入口判断，会让 Windows 带绝对 boundary 或相对 subdir 的路径契约继续错误。

## 2. 必读与基线

开始前完整读取：

1. `docs/fixes/handoffs/CODEX_TASK_10.md`
2. `docs/fixes/handoffs/GROK_COMPLETION_9_REWORK_2.md`
3. `docs/fixes/PRE_MERGE_GATES.md` §2
4. `omnigent/server/routes/_workspace_validation.py`
5. `omnigent/server/routes/sessions.py` 中 `_validate_session_workspace()`
6. `tests/server/routes/test_workspace_validation.py`
7. `tests/server/routes/test_workspace_validation_helpers.py`

开始前记录 `git status --short --branch`、HEAD 和以下现状 blob；不匹配时停止并报告，不得自行恢复工作树：

| 文件 | 开始前 blob |
|---|---|
| `omnigent/server/routes/_workspace_validation.py` | `7401b7422644f2fb38a57cd8a492194a6bfb8cd0` |
| `omnigent/server/routes/sessions.py` | `fb77bc23147828eec70a1c50765dd5c754503241` |
| `tests/server/routes/test_workspace_validation.py` | `c23001c441cb22130d09e4d6cd97151ee5d22824` |
| `tests/server/routes/test_workspace_validation_helpers.py` | `1820f67f6a6143900db65ec1015e332bff7be37a` |

## 3. 精确允许文件

只允许修改：

1. `omnigent/server/routes/_workspace_validation.py`
2. `omnigent/server/routes/sessions.py`，且仅限 `_validate_session_workspace()` 的 absolute-path 判断、相邻 import/docstring
3. `tests/server/routes/test_workspace_validation.py`
4. `tests/server/routes/test_workspace_validation_helpers.py`

只在确实需要覆盖 route 层重复 guard 时允许新建：

5. `tests/server/routes/test_sessions_workspace_validation.py`

只允许新建完成报告：

6. `docs/fixes/handoffs/HERMES_COMPLETION_10.md`

不得修改任何其它文件。若 route 层测试可清晰放入现有测试文件，不要为了目录整洁创建新文件。

## 4. 先写失败测试并保留真实 RED

在任何生产代码修改前补齐下列行为测试。

### 4.1 Windows drive-absolute 主路径

在 `tests/server/routes/test_workspace_validation.py` 增加：

- `test_windows_drive_absolute_workspace_accepted`
- workspace 与 host canonical 均使用类似 `C:\Users\runner\project` 的 Windows drive-absolute 路径；`spec_cwd="."`。
- 期望返回 host 给出的 canonical path，且发给 `host.stat` 的原路径不被改写成 `/mnt/c/...` 或斜杠替换版本。

当前实现的预期 RED：抛出 `WorkspaceValidationError`，消息包含：

```text
workspace must be an absolute path starting with /
```

### 4.2 route 层重复 guard

覆盖 `_validate_session_workspace()`：Windows drive-absolute workspace 必须能继续进入共享 validator，而不是在 `sessions.py` 提前 400。

推荐测试名：

`test_validate_session_workspace_accepts_windows_drive_absolute_path`

可用最小 fake/monkeypatch 捕获传给 `validate_workspace()` 的参数；不得启动 server、host 或真实 runner。当前实现应以同一错误真实 RED。

### 4.3 Windows boundary

在 `tests/server/routes/test_workspace_validation_helpers.py` 为 `_is_subpath_of()` 增加至少以下用例：

- Windows 同一路径：接受。
- Windows 子目录：接受。
- Windows drive letter/路径大小写不同但语义相同：接受。
- prefix collision（如 `C:\repo2` 对 `C:\repo`）：拒绝。
- 不同 drive：拒绝。
- POSIX 现有行为保持。

至少“Windows 子目录”在当前实现必须真实 RED；不得先改实现再补测试。

在 `tests/server/routes/test_workspace_validation.py` 再增加一条通过 `validate_workspace()` 的 Windows boundary 正向用例，证明不是只测 private helper。

### 4.4 Windows `./subdir`

增加一条 Windows canonical workspace + `spec_cwd="./config"` 用例：validator 应向 host stat 发送 Windows host 可用的子路径并返回 workspace canonical path。

测试必须防止以下伪修复：

- 把 drive path 转成 `/mnt/c/...`；
- 依赖 server 本机 `Path.resolve()`；
- 仅删除入口 guard，但仍构造错误的跨平台子路径。

### 4.5 必须继续拒绝的形状

保留现有 relative/tilde 测试，并明确增加或参数化验证：

- `some/relative`：拒绝；
- `~/projects`：拒绝；
- `C:relative`（drive-relative）：拒绝；
- `\rooted-without-drive`（仅当前 drive 根相对，不是 fully-qualified）：拒绝。

不要把“含冒号”或“含反斜杠”当成绝对路径判据。

### 4.6 RED 命令与记录

先只运行新增测试：

```powershell
$env:PYTHONPATH=''
uv run pytest -q tests/server/routes/test_workspace_validation.py -k "windows"
uv run pytest -q tests/server/routes/test_workspace_validation_helpers.py -k "windows"
uv run pytest -q tests/server/routes/test_sessions_workspace_validation.py -k "windows"
```

若没有新建第三个测试文件，删除第三条命令并在报告中说明 route 层用例所在文件。

`HERMES_COMPLETION_10.md` 必须逐条记录命令、退出码、失败 nodeid 和能够证明旧行为的关键错误。collection error、手工推断或 Grok 的 Gate 日志不能冒充本阶段 RED。

## 5. 最小改法

仅在真实 RED 后实施：

1. 在 `_workspace_validation.py` 建立一个无文件系统访问的共享路径形状判断，使用 `pathlib.PurePosixPath` / `pathlib.PureWindowsPath` 或等价纯语法方法：
   - 接受 POSIX absolute；
   - 接受 Windows drive-absolute 与完整 UNC absolute；
   - 拒绝 relative、tilde、drive-relative 与仅根相对 Windows 路径。
2. `validate_workspace()` 与 `_validate_session_workspace()` 必须调用同一判断，不能留下两个不同契约。
3. `_is_subpath_of()` 根据 canonical path 的同一 flavor 比较：
   - Windows 比较遵守 Windows 路径大小写与分隔符语义；
   - POSIX 保持大小写敏感；
   - 两种 flavor 或不同 drive 不得互相判为子路径；
   - 继续防止 prefix collision。
4. `./subdir` 的 host stat 路径按 canonical workspace 的 flavor 拼接；不要调用 server 本机文件系统解析或检查该路径。
5. 用户输入 workspace 仍原样发给目标 host；最终仍只存储 host 返回的 `canonical_path`。不要自行转换 drive、UNC、slash 或映射到 WSL。
6. 只更新与上述契约直接冲突的注释/docstring；不做顺手重构。

如果发现必须修改 HostHello wire protocol、数据库 schema、host frame、runner 启动协议或前端，立即停止并在报告中写为阻塞项；这些都超出本卡允许范围。

## 6. GREEN 与影响测试命令

最小修复后按顺序运行并记录真实 summary/exit：

```powershell
$env:PYTHONPATH=''

uv run pytest -q tests/server/routes/test_workspace_validation.py -k "windows"
uv run pytest -q tests/server/routes/test_workspace_validation_helpers.py -k "windows"
uv run pytest -q tests/server/routes/test_sessions_workspace_validation.py -k "windows"

uv run pytest -q tests/server/routes/test_workspace_validation.py tests/server/routes/test_workspace_validation_helpers.py
uv run pytest -q tests/server/routes/test_sessions_crud.py tests/server/integration/test_host_session_binding.py
uv run pytest -q tests/host/test_connect.py -k "stat"

uv run pytest -q tests/runner/test_session_workspace_cache.py tests/runner/test_session_resources.py::test_failed_session_snapshot_is_not_cached_and_retries tests/runner/test_app_codex_native_model.py tests/runner/test_runner_idle_active_work.py tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_fires_hook_and_awaits_inflight_task tests/runner/transports/ws_tunnel/test_serve.py::test_graceful_drain_bounded_when_task_never_finishes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_once_graceful_shutdown_returns_and_closes tests/runner/transports/ws_tunnel/test_serve.py::test_serve_tunnel_stops_reconnecting_after_graceful_shutdown

uv run ruff check omnigent/server/routes/_workspace_validation.py omnigent/server/routes/sessions.py tests/server/routes/test_workspace_validation.py tests/server/routes/test_workspace_validation_helpers.py tests/server/routes/test_sessions_workspace_validation.py
git diff --check
```

命令须按实际文件存在性调整：未创建 `test_sessions_workspace_validation.py` 时，从 pytest/Ruff 命令删除该路径并说明替代覆盖位置。不得因环境污染把失败删去；如本机必须保留 `$env:PYTHONPATH=''`，如实记录。

本阶段定向 GREEN 不是 Gate 2。不得运行真实 CLI smoke、Gate 1、Gate 2、全仓 pytest 或浏览器 E2E。

## 7. 保护核对

结束时执行并记录：

```powershell
git rev-parse HEAD
git hash-object tests/runner/test_session_workspace_cache.py
git hash-object tests/runner/test_app_codex_native_model.py
git hash-object tests/runner/test_runner_idle_active_work.py
git hash-object tests/runner/transports/ws_tunnel/test_serve.py
git status --short --branch
git diff -- omnigent/server/routes/_workspace_validation.py omnigent/server/routes/sessions.py tests/server/routes/test_workspace_validation.py tests/server/routes/test_workspace_validation_helpers.py tests/server/routes/test_sessions_workspace_validation.py
```

期望保护值：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- workspace blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`
- model blob：`be43ec45816e8ece4192822506df8072580910e0`
- idle blob：`58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
- serve blob：`6116218097f2352c467524fd0ddf0838315aa524`

还须确认阶段 1/3/5累计改动、`docs/fixes/STATUS.md`、`docs/fixes/PRE_MERGE_GATES.md`、`docs/fixes/POST_FIX_HANDOFF_PROMPT.md` 与全部旧 handoff 未被清理、覆盖或格式化。

## 8. 禁止项

- 不得改 Gate 政策、STATUS、POST_FIX、旧 handoff 或旧 evidence。
- 不得修改 `omnigent/host/frames.py`、host protocol、数据库、前端、依赖、lockfile或CI。
- 不得把 Windows 路径转换为 WSL/POSIX 路径；不得用 server 本机文件系统验证 remote host 路径。
- 不得通过删除 absolute-path 校验、接受任意字符串或放宽相对路径来变绿。
- 不得修改测试预期以接受旧 400；不得删减 POSIX、boundary、symlink 或相对路径保护测试。
- 不得运行真实 Gate 2；不得复用、追加或改写 `20260730-0202-...-r2` evidence。
- 不得顺手修其它 Gate 2、native prompt、host daemon 或全仓失败。
- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得 commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得宣称 Gate 2 PASS、Gate 1全仓 GREEN或可 merge。

## 9. 完成报告

只新建 `docs/fixes/handoffs/HERMES_COMPLETION_10.md`，必须包含：

1. 根因和最终路径契约。
2. 开始/结束 HEAD、git status 与目标文件范围。
3. 每条新增测试及其真实 pre-fix RED 命令、失败 nodeid、exit、关键错误。
4. 精确生产/test diff 摘要；说明为何不需要 wire protocol 或 schema 变化。
5. 每条 GREEN、影响套件、保护回归、Ruff、`git diff --check` 命令与真实结果。
6. 四个保护 blob 与 r05/旧 handoff 未变的核对。
7. 剩余风险和未完成项。
8. 明确：Gate 1仍为相对 PASS、非全仓 GREEN；Gate 2仍为 FAIL、尚未重跑；不可 merge。

## 10. 完成标准

只有以下全部满足，阶段 10才算完成：

1. 真实 RED 证明 drive-absolute 在两层入口被旧 POSIX-only 契约拒绝，并证明 Windows boundary 至少一项旧行为失败。
2. POSIX absolute、Windows drive-absolute 和完整 UNC absolute 被正确分类；四类非绝对形状继续拒绝。
3. Windows canonical boundary 的相等、子目录、大小写、prefix collision、跨 drive 行为均有测试。
4. Windows `./subdir` 使用 host 路径语义；输入和 canonical 路径不被擅自转换。
5. 全部第6节实际适用命令通过；任何跳过、失败或未执行均如实记录并交回 Codex，不得自行降级完成标准。
6. 改动严格限于第3节；HEAD、四个保护 blob、r05和旧 handoff保持。
7. 已写 `HERMES_COMPLETION_10.md`；无 commit/push/merge/tag。
8. 未执行或判定 Gate 2；未宣称可 merge。

完成后停止，交回 Codex只读验收。Codex验收通过后另发独立审查卡；在独立审查和全新 Gate 2 RUN 前，不得继续推进。
