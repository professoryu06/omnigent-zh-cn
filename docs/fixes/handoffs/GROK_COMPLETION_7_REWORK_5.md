# GROK COMPLETION 7 REWORK 5 — 审计惰性 pytest tmux 后隔离 HOME 双侧 Gate 1

**执行者：** Grok（Gate 1 执行者，非独立审查者）  
**日期：** 2026-07-29  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_7_REWORK_5.md`  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 最终判定

### Gate 1 = **PASS（相对 main）**

| 条件 | 结果 |
|------|------|
| r5 INVALID 已由 Codex 验收；blanket quiescence 过宽 | 接受；本轮改为精确 tmux 分类 |
| 惰性 pytest tmux 精确分类 | **白名单通过**；**未** TERM/KILL/tmux kill-server |
| host/server 仅精确 PID 清理 | **OK**（TERM only，未 KILL） |
| 隔离 HOME：两侧运行前与空 seed cmp | **OK** |
| 身份 / 包列表 / receipt / 四保护 | **OK** |
| baseline 全仓完成 + JUnit 可解析 + tee 0 | **OK**（exit 1） |
| candidate 全仓完成 + JUnit 可解析 + tee 0 | **OK**（exit 1） |
| `new-failures.txt` | **空**（candidate ⊆ baseline） |
| `baseline-known-failures.md` | **已写**（126 个 nodeid 逐项） |

**不是** PASS（绝对）：candidate 非 exit 0，有 junit fail/error。  
**不是** FAIL：无 candidate 新增失败。  
**不是** INVALID：双侧完整、tee 0、JUnit 有效、分类/HOME/身份有效。

**Gate 2：仍未执行、未判定。**  
**不可 merge**；本 PASS **仅** 待 Codex 只读验收后策划 Gate 2。

---

## 2. RUN_ID 与证据路径

| 项 | 值 |
|----|-----|
| **RUN_ID** | `20260729-1715-dc83140-grok-r6` |
| **Linux evidence** | `/tmp/omnigent-premerge-evidence/20260729-1715-dc83140-grok-r6` |
| **Windows evidence** | `C:\Users\Administrator\gate1-evidence\20260729-1715-dc83140-grok-r6` |
| **SEED_HOME** | `/tmp/omnigent-gate1-home-20260729-1715-dc83140-grok-r6-seed` |
| **RUN_HOME** | `/tmp/omnigent-gate1-home-20260729-1715-dc83140-grok-r6-active` |

未覆盖 r2–r5。  
未拼接 r2–r5 全仓结果；失败比较 **仅** 本轮 r6 双侧 JUnit。  
Linux/Windows 内容已全量复制；`linux-evidence.sha256` / `windows-evidence.sha256` 已生成（清单文件自身哈希因包含时机不同可差 1 项，业务文件已同步）。

---

## 3. r5 根因与本轮策略

r5 将 **任意** cwd=树 的进程视为阻塞，把历史 `test_server_survives_inner_pro*` 惰性 tmux 当成阻塞 → 全仓未开。  

本轮 `classify_tree_processes`：**完全匹配** 的惰性 pytest tmux 写入 `*-allowed-pytest-tmux.txt` 且 **不阻塞**；任何偏差写入 `*-blocking-processes.txt` → INVALID。  
**禁止** 终止这些白名单 tmux。

---

## 4. 白名单 tmux（预跑示例）

`pre-baseline-processes-allowed-pytest-tmux.txt`（2 条，blocking=0）：

| PID | PPID | STATE | EXE | SOCKET | CHILDREN |
|-----|------|-------|-----|--------|----------|
| 36338 | 30064 | S | `/usr/bin/tmux` | `…/pytest-3/test_server_survives_inner_pro0/tmux.sock` | 0 |
| 61722 | 59920 | S | `/usr/bin/tmux` | `…/pytest-6/test_server_survives_inner_pro0/tmux.sock` | 0 |

均满足：cwd=baseline 树、socket 模式、`remain-on-exit` / `exit-empty off` / `new-session -d -s main` / `sh -c 'exit 0'`、无子进程、休眠。  

`pre-candidate-processes`：allowed=1，blocking=0。  

**明确：白名单 tmux 未收到任何信号；未调用 `tmux kill-server`。**

各阶段 classify：`blocking=0`（pre / post-baseline / candidate-before / post-candidate）。

---

## 5. host/server 精确清理

| 阶段 | 结果 |
|------|------|
| pre-baseline / pre-candidate | 清理函数执行；无多余 multiplicity |
| post-baseline | TERM 76961/76960 → EXITED_AFTER_TERM_NO_KILL |
| post-candidate | TERM 91991/91990 → EXITED_AFTER_TERM_NO_KILL |

- 先 server 后 host；仅 PID 级 **TERM**；未 KILL  
- **未** pkill / killall / 负 PID / 组 kill / WSL shutdown  
- 端口 6767 在 classify 各检查点为空  

---

## 6. 隔离 HOME

| 检查 | 结果 |
|------|------|
| seed 仅空 `.config`/`.cache`/`.local` | 是 |
| baseline 运行前 home-before **cmp** seed | **OK** |
| candidate 运行前 home-before **cmp** seed | **OK** |
| 两侧同一绝对 `RUN_HOME` | 是 |
| 复制真实 HOME / 密钥 / DB | **否** |

---

## 7. 身份与依赖

| 检查 | 结果 |
|------|------|
| baseline HEAD | `81594243f7a17303b9ba477b938ac323f938c2e4` |
| candidate HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| status/patch/manifest/blob vs r2 | cmp OK |
| r3 receipt 七项哈希 | cmp OK |
| 四保护 blob | `02cce3ca` / `be43ec45` / `58b24b7d` / `61162180` |
| baseline/candidate 包列表 | cmp OK |
| environment.txt | 已记录 boot_id / uname / os-release / uv / python |

**未** re-sync / 安装依赖 / 重建树。  
**未** 重跑定向 / Ruff / diff-check / Gate 2。

---

## 8. 双侧全仓结果（仅 r6）

### 命令（两侧相同模板）

```bash
HOME="$RUN_HOME" XDG_CONFIG_HOME=… XDG_CACHE_HOME=… XDG_DATA_HOME=… \
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=60s 21600s \
  uv run pytest -q --color=no \
    --timeout=300 --timeout-method=signal \
    --junitxml=…/{baseline,candidate}-junit.xml
```

- **每测试 300s**；**CLI** `timeout_method=signal`  
- **禁止** `-p no:timeout`；**未**提高 300  

### 时间线（+08:00）

| 事件 | 时间 |
|------|------|
| baseline START | 17:15:54 |
| baseline END | 18:31:35（~1h16m） |
| candidate START | 18:31:36 |
| candidate END | 19:49:58（~1h18m） |

### Summary

| | baseline | candidate |
|--|----------|-----------|
| COMMAND_EXIT | **1** | **1** |
| TEE_EXIT | **0** | **0** |
| pytest summary | **123 failed**, 14926 passed, 103 skipped, 7 xfailed, 237 warnings, **3 errors**, 3 subtests, 4 rerun in **4391.56s** | **123 failed**, 15006 passed, 103 skipped, 7 xfailed, 237 warnings, **3 errors**, 3 subtests, 4 rerun in **4559.10s** |
| JUnit | 存在、非空 | 存在、非空 |
| JUnit parse | **junit-ok** | **junit-ok** |
| fail-ids（dotted `classname::name`） | **126** | **126** |

### 失败比较

```text
comm -13 baseline-fail-ids.txt candidate-fail-ids.txt → new-failures.txt
```

- **new-failures.txt：空**  
- candidate 失败集 **⊆** baseline（且条数相同 126）  

### baseline-known-failures

文件：`baseline-known-failures.md`（645 行）  

对 **每一个** 本轮 baseline fail-id：

- type: r6 baseline JUnit failure/error  
- environment: WSL + 隔离空 seed 恢复的同一 `RUN_HOME` + baseline 树 main HEAD + 与 candidate 相同 venv 包列表  
- evidence: 仅本 RUN_ID 的 `baseline-junit.xml` / `baseline-pytest.txt`  

依据为 **同环境双侧对照**，不是“口头说 main 也失败”。相对 PASS 的共享环境失败集由此成立。

---

## 9. 判定对照 §8

| 规则 | 本轮 |
|------|------|
| PASS（绝对） | 否 — candidate exit≠0 |
| **PASS（相对 main）** | **是** — 双侧完整；tee 0；JUnit 有效；new-failures 空；known 逐项；身份/HOME/分类有效 |
| FAIL | 否 — 无新增 candidate 失败 |
| INVALID | 否 |

---

## 10. 源工作树保护

| 项 | 结果 |
|----|------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| 四保护 blob | 未变 |
| 源码/tests/config/lockfile | **未改** |
| 本轮唯一源树交付 | `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_5.md` |
| 旧 handoff / r2–r5 | **未改** |

---

## 11. 禁止项遵守

- [x] 未杀白名单 tmux；未 tmux kill-server  
- [x] 无 pkill/killall/负 PID/组 kill/WSL shutdown  
- [x] host/server 仅精确 PID TERM  
- [x] 未碰真实 HOME 密钥/DB  
- [x] 失败比较仅 r6 JUnit  
- [x] 未 `-p no:timeout`、未提高 300s  
- [x] 未重跑定向/Ruff/Gate 2  
- [x] 未 commit/push/merge/tag  

---

## 12. 交回 Codex

**Gate 1 = PASS（相对 main）。**  

请 Codex **只读验收** 后决定是否生成 Gate 2 任务卡。  
**Gate 2 仍未执行、未判定；本结论不代表可 merge。**
