# HERMES_DIAGNOSIS_25 — Windows 路径测试债务 + Codex 隔离契约只读审查

**RUN_ID**: `20260731-115300-dc83140-hermes-diag25-r1`
**日期**: 2026-07-31
**角色**: Hermes 只读审查，不修改源码
**范围**: `tests/host/test_connect.py` (25 failed / 48 passed) + `tests/inner/test_codex_runtime_isolation.py` (25 passed)

---

## 1. 测试现状

| 套件 | 结果 | 说明 |
|------|------|------|
| `tests/inner/test_codex_runtime_isolation.py` | **25 passed** ✅ | CODEX_TASK_23 隔离契约全绿 |
| `tests/host/test_connect.py` | **25 failed / 48 passed** ❌ | Windows 平台债务，非隔离修复引入 |

## 2. 根因分类

### RC-1: Windows 路径分隔符（6 个失败）

**症状**: 测试期望 `~/.omnigent/logs/runner/runner-xxx.log`（正斜杠），实际输出 `~/.omnigent\logs\runner\runner-xxx.log`（反斜杠）。

**根因**: `omnigent/host/connect.py:116`

```python
def _display_log_path(path: Path) -> str:
    return f"~/{path.relative_to(Path.home())}"
```

`Path.relative_to()` 在 Windows 上返回 `WindowsPath`，其 `str()` 使用 `\`。f-string 拼接后变成 `~/` + `logs\runner\xxx.log`。

**受影响测试**:
- `test_handle_launch_prints_exact_runner_log_path`
- `test_handle_launch_immediate_exit_reports_exit_code_and_log_tail`
- `test_handle_stat_expands_tilde`
- `test_handle_list_dir_expands_tilde`
- `test_handle_create_dir_expands_tilde`
- `test_run_host_process_announces_session_log_dir_on_start`

**最小修复**:

```python
def _display_log_path(path: Path) -> str:
    try:
        return "~/" + path.relative_to(Path.home()).as_posix()
    except ValueError:
        return str(path)
```

一行改动：`str(relative)` → `relative.as_posix()`。

---

### RC-2: `os.WNOHANG` / `os.waitpid` 在 Windows 不存在（18 个失败）

**症状**: `AttributeError: module 'os' has no attribute 'WNOHANG'`

**根因**: `omnigent/host/connect.py:775-777`

```python
if hasattr(os, "waitid") and hasattr(os, "P_ALL"):
    return self._reap_orphans_waitid()
return self._reap_orphans_waitpid()  # ← Windows 走这里
```

`_reap_orphans_waitpid()` 在 line 842 调用 `os.waitpid(-1, os.WNOHANG)`。Windows 的 `os` 模块没有 `WNOHANG`（也没有 `waitpid(-1)` 语义）。

**影响链**: `_reap_orphans_once()` 在 `run()` (line 724) 中被调用 → 任何走 `run()` 或 `run_host_process()` 的测试都会触发 → login redirect 重试、4xx 永久错误、transient 重连、fatal exit 等 18 个测试全部挂。

**受影响测试**:
- `test_reap_orphans_reaps_orphaned_children`
- `test_reap_orphans_never_steals_tracked_runner_exit_code`
- `test_run_retries_on_login_redirect`
- `test_login_redirect_prints_warning_to_terminal`
- `test_fresh_host_fails_loud_after_persistent_login_redirects`
- `test_login_redirect_streak_resets_on_other_transient_errors`
- `test_connected_host_retries_login_redirects_indefinitely`
- `test_run_fails_loud_on_permanent_4xx[401/403/404]`
- `test_auth_rejection_suggests_omnigent_login[401/403]`
- `test_non_auth_permanent_4xx_omits_login_hint`
- `test_run_reconnects_on_transient_upgrade_failure[408/429/500/503]`
- `test_run_host_process_exits_nonzero_on_fatal`

**最小修复**:

```python
def _reap_orphans_once(self) -> int:
    if self._owned_subprocess_ops > 0:
        return 0
    if not hasattr(os, "waitpid"):
        return 0  # Windows: no POSIX orphan reaping
    if hasattr(os, "waitid") and hasattr(os, "P_ALL"):
        return self._reap_orphans_waitid()
    return self._reap_orphans_waitpid()
```

一行 guard：`if not hasattr(os, "waitpid"): return 0`。Windows 没有 POSIX 孤儿进程概念，`subprocess.Popen` 自行管理子进程生命周期，跳过 reaper 是正确行为。

---

### RC-3: Windows `mkdir` 语义差异（1 个失败）

**症状**: `test_handle_create_dir_parent_is_file_returns_error` 期望 `status == "ok"`，实际 `"failed"`。

**根因**: 测试逻辑是"父路径是文件时创建子目录应返回 error（不是 failed）"。Windows 上 `Path.mkdir(parents=True)` 在父路径是文件时抛出的异常类型或消息与 Linux 不同，导致 handler 走了 `failed` 分支而非 `error` 分支。

**受影响测试**:
- `test_handle_create_dir_parent_is_file_returns_error`

**最小修复**: 需要检查 `handle_create_dir` 的异常处理是否覆盖了 Windows 的 `NotADirectoryError` / `OSError [WinError 267]`。或者测试本身在 Windows 上应 skip（如果 upstream 只支持 POSIX 语义）。

---

## 3. Codex 隔离契约状态

| 检查项 | 状态 |
|--------|------|
| `tests/inner/test_codex_runtime_isolation.py` | 25 passed ✅ |
| 私有 CODEX_HOME 创建 | ✅ |
| tomlkit 清洗（移除 openai_base_url/model） | ✅ |
| auth.json 桥接（symlink） | ✅ |
| `-c model="gpt-5.6-sol"` argv | ✅ |
| env denylist（OPENAI_BASE_URL/OPENAI_API_BASE） | ✅ |
| gateway/订阅互斥 | ✅ |
| 代理注入（HTTPS_PROXY/HTTP_PROXY/ALL_PROXY） | ✅ 代码存在 |
| `features.network_proxy` + `network_proxy.proxy_url` config override | ✅ 代码存在 |

**结论**: 隔离契约完整，25 个测试全绿。`test_connect.py` 的 25 个失败与隔离修复无关，是 pre-existing Windows 平台债务。

## 4. 测试矩阵

| 修复 | 影响范围 | 预期结果 | 风险 |
|------|----------|----------|------|
| RC-1: `as_posix()` | `_display_log_path` 1 行 | 6 个路径测试转绿 | 极低（纯显示） |
| RC-2: `hasattr(os, "waitpid")` guard | `_reap_orphans_once` 1 行 | 18 个 run/reap 测试转绿 | 低（Windows 无 POSIX 孤儿） |
| RC-3: mkdir 异常处理 | `handle_create_dir` 或 test skip | 1 个测试转绿 | 低 |
| 合计 | 3 处改动 | 25 failed → 0 failed | — |

## 5. 方案建议（给 Grok 实施卡）

### 推荐：单 PR 修复全部三类

**改动文件**:
1. `omnigent/host/connect.py` — 2 行（RC-1 + RC-2）
2. `omnigent/host/connect.py` 或 `tests/host/test_connect.py` — RC-3（需进一步确认 handler 逻辑）

**验证命令**:
```bash
PYTHONPATH="" .venv/Scripts/python.exe -m pytest tests/host/test_connect.py tests/inner/test_codex_runtime_isolation.py -q
```

**预期**: 73 passed（48 + 25）

**约束**:
- 不改隔离契约逻辑
- 不改 `_clean_codex_env` / `_configure_codex_subscription_proxy`
- 不改 TUN / OpenCodex / 10100
- 不跑 full-run
- 不 commit/push/merge（除非任务卡授权）

### 备选：RC-3 单独处理

如果 RC-3 的 handler 逻辑涉及 upstream 行为差异（Linux 返回 `FileExistsError`，Windows 返回 `NotADirectoryError`），可能需要：
- 在 handler 中 catch `NotADirectoryError` 并返回 `error` 而非 `failed`
- 或者在测试中 `@pytest.mark.skipif(sys.platform == "win32", ...)`

## 6. Gate 边界声明

- 本审查**不是** Gate 2 验收
- 隔离契约 25 passed 证明 CODEX_TASK_23 实现正确
- `test_connect.py` 25 failed 是 pre-existing Windows 债务，不阻塞隔离修复
- Gate 2 仍为 **NOT PASS**（Codex CLI 网络层问题未解决）
- 修复 test_connect.py 后 Gate 1 可从"相对 main PASS"升级为"绝对 PASS"

## 7. 与 CODEX_TASK_24 网络问题的关系

`test_connect.py` 的失败与 Codex CLI 网络问题（10106/11003）**完全无关**：
- RC-1/RC-2/RC-3 都是 host 进程管理层面的 Windows 兼容性
- Codex CLI 网络问题在 `codex_executor.py` 的子进程启动层
- 修复 test_connect.py 不会改善也不会恶化 Codex CLI 的网络行为
