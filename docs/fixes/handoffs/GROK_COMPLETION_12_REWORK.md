# GROK COMPLETION 12 REWORK — r3 工作树 Codex home 精确清理

**执行者：** Grok（清理返工；不重跑 Gate）  
**日期：** 2026-07-30  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_12_REWORK.md`  
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 唯一结论

### **`REWORK_CLEANUP_OK`**

| 项 | 结果 |
|----|------|
| 精确目标 | `…\.codex-tmp\omnigent-codex-home-qun0egm8` **已删除** |
| 父目录 `.codex-tmp` | **保留** |
| 链接目标 / credential | **未跟随、未读取**（仅删 reparse 本身） |
| r3 四态 | **永久 INVALID**（本清理不改变） |
| Gate 2 PASS / merge | **否** |

---

## 2. 外部清理证据

**路径：**  
`C:\Users\Administrator\gate2-evidence\cleanup-r3-codex-home-20260730-132925\`

| 文件 | 用途 |
|------|------|
| `identity-start.txt` / `identity-end.txt` | HEAD 与 blob |
| `git-status-start.txt` / `git-status-end.txt` | 仓库状态 |
| `path-safety.txt` / `before-metadata.txt` | 删除前归属与数量 |
| `process-check.txt` | PID/端口/命令行 |
| `remove-actions.txt` | 逐步删除（无 Target/正文） |
| `after-metadata.txt` | 删除后验证 |
| `CLEANUP_SUMMARY.txt` | **CLEANUP_OK=true** |

---

## 3. 删除前安全检查摘要

固定路径：

- `WORKTREE` = `F:\codex-ai\git项目部署\tmp\omnigent-review`
- `CODEX_TMP` = `{WORKTREE}\.codex-tmp`
- `TARGET` = `{CODEX_TMP}\omnigent-codex-home-qun0egm8`

| 检查 | 结果 |
|------|------|
| 路径归属（worktree / 父级 / 叶名精确） | 通过 |
| TARGET 普通目录、非 reparse | 通过 |
| 创建时间 UTC 秒 | `2026-07-30T04:36:39` 所在秒 | 通过 |
| 后代 17 / reparse 15 / 普通文件 1（`config.toml`） | 通过 |
| 普通子目录仅 `skills` | 通过 |
| `auth.json` reparse；`LinkType=SymbolicLink` | 通过（**未读 Target**） |
| 其余 reparse 均在 `skills\` 下 | 通过 |
| r3 PID 2820/21420/40232/40612 | **DEAD** |
| 端口 64774 | **无 listen** |
| 命令行含目标路径/叶名/r3 RUN/64774 的非 shell 进程 | **0** |

任一失败则不会删除。本轮全部满足后才删除。

---

## 4. 精确删除步骤

顺序（`System.IO` 删除 **链接/文件本身**；非 `Remove-Item -Recurse` 父目录；非通配符）：

1. 逐个删除 `skills\` 下 14 个 **Directory+ReparsePoint**（`Directory.Delete(path, false)`）→ 全部 OK  
2. 删除 `auth.json` 符号链接（`File.Delete`，不跟随）→ OK  
3. 删除普通文件 `config.toml`（不读内容）→ OK  
4. 确认 `skills` 空后非递归删目录 → OK  
5. 确认 TARGET 空后非递归删 TARGET → OK  
6. **未**删除 `.codex-tmp` 父目录  

见 `remove-actions.txt`（仅叶名/类型/OK，无链接 Target、无 config 正文）。

说明：非交互 PowerShell 下 `Remove-Item` 对 reparse 会触发 Prompt 失败；改用 **.NET 单路径删除**，范围仍为已验证的精确路径，**未**扩大到父目录或其它 `omnigent-codex-home-*`。

---

## 5. 删除后验证

| 检查 | 结果 |
|------|------|
| TARGET 存在 | **false** |
| `.codex-tmp` 存在 | **true**（父保留） |
| r3 四 PID | 仍 DEAD |
| 64774 listen | false |
| 进程匹配 | 0 |
| r3 / 0202 evidence 近 10 分钟 mtime 变更 | **0**（旧 evidence 未改） |

`CLEANUP_SUMMARY.txt`：

```text
CLEANUP_OK=true
target_removed=true
parent_preserved=true
credential_target_untouched=true
run_process_matches=0
port_64774_listeners=0
old_evidence_unchanged=true
```

---

## 6. 对 r3 报告的补正（不改写旧文件）

**未修改** `GROK_COMPLETION_12.md` 与 r3 evidence 任何文件。

补正说明：

1. 原 `cleanup.txt` 的 `leftover_after=0` **仅**覆盖驱动枚举的 **进程 / RUNTIME_ROOT / 端口**，**不足以**证明工作树忽略目录无运行残留。  
2. r3 `leak-scan` **只**扫 evidence 根，**不**覆盖 `.codex-tmp`。  
3. Git 忽略 `.codex-tmp/`，故原 `git status` 看不到该残留。  
4. 本返工 **仅**恢复工作树卫生；**不**把 r3 提升为 FAIL/PASS。

### r3 永久保持

| 项 | 值 |
|----|-----|
| Gate 2 | **INVALID** |
| C | timeout=true，cli_exit=-1 不可信，session_id=UNKNOWN |
| 0202 旧 400 | 未见但 **未**证明消除 |
| 后五轮 | 未执行 |

---

## 7. 身份与 git

| 项 | 结果 |
|----|------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| 阶段 10 四 blob | 匹配任务卡 |
| 四保护 blob | 匹配 |
| 仓库交付 | **仅新建**本文件 `GROK_COMPLETION_12_REWORK.md` |
| 旧 evidence / 旧 handoff | **未修改** |

---

## 8. 下次 Gate 2 要求（给 Codex 策划）

新 RUN 必须：

1. 开始/结束快照工作树 `.codex-tmp` 叶名清单；  
2. finally 中精确清理**本 RUN 新建**的 `omnigent-codex-home-*`（路径归属检查同本卡）；  
3. 不得跟随 reparse Target；不得删整个 `.codex-tmp` 除非策略另定。

---

## 9. 禁止项遵守

- 未读 auth 链接目标、credential 值、config 正文  
- 未删 `.codex-tmp` 父目录、未通配符、未 git clean  
- 未改源码/tests/政策/STATUS/旧 handoff/旧 evidence  
- 未跑 Gate/pytest/Ruff/CLI  
- 未 commit/push/merge/tag  
- **未**将清理写成 Gate 2 PASS 或可 merge  

---

## 10. 交回 Codex

| 项 | 状态 |
|----|------|
| 返工结论 | **REWORK_CLEANUP_OK** |
| r3 Gate 2 | **仍 INVALID** |
| Gate 1 | PASS（相对 main）；非全仓 GREEN |
| Merge | **不可 merge** |

**停止。** 不得自行开始下一个 Gate 2 RUN。
