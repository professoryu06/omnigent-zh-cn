# GROK COMPLETION 7 REWORK 4 — 隔离 HOME 的 Gate 1 双侧重跑

**执行者：** Grok（Gate 1 执行者，非独立审查者）  
**日期：** 2026-07-29  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_7_REWORK_4.md`  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 最终判定

### Gate 1 = **INVALID**

| 阶段 | 结果 |
|------|------|
| r4 INVALID 已由 Codex 验收 | 接受；拒绝 candidate-only + 共享 HOME 拼接 |
| 精确清理 baseline host/server（60275/60276） | **成功**（仅 TERM，未 KILL） |
| candidate host/server 预清理 | **无匹配进程** |
| 端口 6767 | **空闲**（`no_6767`） |
| `assert_tree_quiescent(baseline)` 预跑 | **失败**：cwd=baseline 树的 **tmux** 残留 |
| 受控 HOME seed | 已创建空 seed；**未**进入全仓 |
| baseline→candidate 全仓 | **未启动** |
| 树身份 / receipt / 四保护 / 包列表 | **通过**（全仓前复核） |

**未** 使用 pkill/killall/负 PID/进程组 kill/WSL shutdown。  
**未** 触碰 `/init`、tmux（禁止终止）。  
**未** 读取/复制/删除真实用户 HOME 的 credentials/数据库/artifacts。  
**未** 拼接 r2/r3/r4 全仓结果。  

**Gate 2：仍未执行、未判定。不可 merge。**

---

## 2. RUN_ID 与证据路径

| 项 | 值 |
|----|-----|
| **RUN_ID** | `20260729-1617-dc83140-grok-r5` |
| **Linux evidence** | `/tmp/omnigent-premerge-evidence/20260729-1617-dc83140-grok-r5` |
| **Windows evidence** | `C:\Users\Administrator\gate1-evidence\20260729-1617-dc83140-grok-r5` |
| **SEED_HOME** | `/tmp/omnigent-gate1-home-20260729-1617-dc83140-grok-r5-seed` |
| **RUN_HOME** | `/tmp/omnigent-gate1-home-20260729-1617-dc83140-grok-r5-active` |

未覆盖 r2/r3/r4。  
双方清单：`linux-evidence.sha256` / `windows-evidence.sha256`。

---

## 3. 拒绝 candidate-only 的依据（任务卡 §2）

r4 已证明：baseline 全仓会向 **真实用户 HOME** 写 `~/.omnigent-zh-cn` 并遗留 host/server。  
在没有 baseline 开跑前 HOME 快照的情况下，仅跑 candidate 再与 r4 baseline 比失败集 **不可审计**。  
本轮设计为：空 HOME seed + 两侧运行前 `restore_run_home` + **完整** baseline→candidate。  
因预跑静默失败，全仓未开，故 **无** 本轮双侧失败集，**不得** 回退到 r4 baseline 做 `comm`。

---

## 4. baseline 残留清理（§5 / §6）

### 4.1 现场重新发现与 `/proc` 身份

`pre-baseline-residue-cleanup-targets.txt`：

| 角色 | PID | PPID | START | CWD | CMD |
|------|-----|------|-------|-----|-----|
| server | **60276** | 60275 | 1759703 | baseline 树 | `…/baseline-…r2/.venv/bin/python -m omnigent.cli server --host 127.0.0.1 --port 6767 …`（DB 在 `~/.omnigent-zh-cn`） |
| host | **60275** | 59920 | 1759674 | baseline 树 | `…/baseline-…r2/.venv/bin/python -m omnigent.host._daemon_entry --local` |

- cwd = baseline 树  
- server PPID = host  
- **未** 将 `/init` 或无关 PID 列入目标  

### 4.2 信号

`pre-baseline-residue-cleanup-signals.txt`：

```text
TERM PID=60276 START=1759703
TERM PID=60275 START=1759674
EXITED_AFTER_TERM_NO_KILL PID=60276
EXITED_AFTER_TERM_NO_KILL PID=60275
```

- 先 server 后 host **TERM**  
- 20s 内退出 → **未 KILL**  
- **未** pkill / killall / 负 PID / 进程组 kill / `wsl --shutdown|--terminate`  

### 4.3 host/server 与端口

- `pre-baseline-residue-processes-after.txt`：**空**  
- `pre-candidate-residue`：无匹配进程  
- finalize 时 `ss`：**无 :6767**  

---

## 5. 静默断言失败原因（阻塞全仓）

`pre-baseline-quiescent-tree-bound-processes.txt` 仍含 **2 个 tmux**（cwd = baseline 树）：

| PID | 说明 |
|-----|------|
| 36338 | `tmux -S /tmp/pytest-of-administrator/pytest-3/test_server_survives_inner_pro0/tmux.sock …` |
| 61722 | `tmux -S /tmp/pytest-of-administrator/pytest-6/test_server_survives_inner_pro0/tmux.sock …` |

任务卡 `assert_tree_quiescent` 要求：任意 `/proc/*/cwd == tree` 的非空 cmdline 进程 → **非空文件 → 失败**。  
任务卡同时 **禁止终止 tmux**。  

因此：

1. 不能 kill 上述 tmux；  
2. 不能在树未静默时开跑全仓；  
3. 按 §6/§9 → **INVALID**，停止。  

这些 tmux 来自历史 pytest（`test_server_survives_inner_pro*`）泄漏，非本轮创建；清理授权 **仅** 覆盖 host/server 模块匹配。

---

## 6. 受控 HOME seed（已创建，未用于全仓）

| 路径 | 状态 |
|------|------|
| `SEED_HOME` | 700；仅空 `.config` / `.cache` / `.local` / `.local/share` |
| `RUN_HOME` | 创建后为空（`rm -rf` 仅在路径校验通过的 active home 上授权；本轮未跑 `restore_run_home` 进入 suite） |

**未** 从真实 HOME 复制任何内容。

---

## 7. 环境与身份复核（全仓前，已通过）

| 检查 | 结果 |
|------|------|
| baseline HEAD | `81594243f7a17303b9ba477b938ac323f938c2e4` |
| candidate HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| status/patch vs r2 | cmp OK |
| tracked/untracked/blob vs r2 | cmp OK |
| r3 receipt 七项哈希 | cmp OK |
| 四保护 blob | `02cce3ca` / `be43ec45` / `58b24b7d` / `61162180` |
| baseline/candidate 包列表 | **cmp OK** |
| WSL environment | 见 `environment.txt` |

**未** re-sync / 安装依赖 / 重建树。  
**未** 重跑定向 / Ruff / diff-check / Gate 2。

---

## 8. 全仓命令（设计意图；实际未执行）

```bash
HOME="$RUN_HOME" XDG_*="$RUN_HOME/..." \
timeout --signal=INT --kill-after=60s 21600s \
  uv run pytest -q --color=no \
    --timeout=300 --timeout-method=signal \
    --junitxml=…/{baseline,candidate}-junit.xml
```

- 顺序 baseline → candidate  
- **禁止** `-p no:timeout`；**禁止** 提高 300s  
- 本轮因 §5 预跑静默失败 **未调用**  

因此无本轮 `*-pytest.txt` / JUnit / fail-ids / `new-failures.txt` 全仓产物。

---

## 9. 判定对照 §9

| 规则 | 本轮 |
|------|------|
| PASS（绝对） | 否 — 无 candidate 全仓 |
| PASS（相对 main） | 否 — 无双侧本轮失败集 |
| FAIL | 否 — 无 candidate 新增失败证据 |
| **INVALID** | **是** — 树未静默（tmux cwd=baseline）；全仓未完成；禁止 kill tmux |

---

## 10. 源工作树保护

| 项 | 结果 |
|----|------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| 四保护 blob | 未变 |
| 源码/tests/config/lockfile | **未改** |
| 本轮唯一源树交付 | `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_4.md` |
| 旧 handoff / r2–r4 | **未改** |

---

## 11. 建议 Codex 后续（Grok 不执行）

1. **另卡**明确授权：如何处理 cwd=树、socket 在 `/tmp/pytest-of-administrator/…` 的 **遗留 tmux**（例如仅当 cmdline/socket 路径匹配 pytest 临时目录时 PID 级 TERM；或重建干净 clone 树）。  
2. 在树静默后，**完整** baseline→candidate 隔离 HOME 重跑（仍不得拼接 r4）。  
3. 产品侧跟踪：pytest 结束后 host/tmux 泄漏（根因修复不在 Gate 执行卡范围）。  

---

## 12. 禁止项遵守

- [x] 仅 PID 级 TERM（未 KILL）  
- [x] 无 pkill/killall/负 PID/组 kill/WSL shutdown  
- [x] 未杀 tmux / init  
- [x] 未碰真实 HOME 密钥与 DB  
- [x] 未拼接旧全仓  
- [x] 未改源码/tests/config  
- [x] 未 commit/push/merge/tag  
- [x] 未跑 Gate 2  

---

**交回 Codex 只读验收。**  
**Gate 1 = INVALID。** Gate 2 未执行、未判定；不可 merge。
