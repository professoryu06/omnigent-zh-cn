# CODEX TASK 3 REWORK 2 — Grok 修正 host 全套退出码证据

**执行者：** Grok（本轮获用户明确授权，只修改阶段 3 交接文档）

**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

**阶段边界：** 阶段 3 的第二次返工，仅修正交接报告中的证据事实；不得修改任何源码、测试或 fixture，不运行测试，不进入阶段 4。Grok 写完后交由 Codex 做只读审查。

## 1. 问题

`docs/fixes/handoffs/HERMES_COMPLETION_3.md` 第 409 行记录：

```text
结果：25 failed, 45 passed, 42 warnings，exit 0（pytest 不因既有失败返回非零）。
```

该记录与 pytest 实际退出状态矛盾，并违反 `CODEX_TASK_3_REWORK.md` 第 111、119—120 行“平台既有失败必须按实际非零退出码记录”的完成标准。

Codex 在 Windows、Python 3.11.15、pytest 9.0.3，并把 `C:\Program Files\Git\usr\bin` 加入 `PATH` 以提供 `sh.exe` / `sleep.exe` 后独立复跑同一套件，得到：

```text
25 failed, 45 passed, 42 warnings
HOST_FULL_EXIT=1
```

三个 watcher 定向测试在同一类具备 `sh` / `sleep` 的环境仍为 `3 passed`、exit 0；代码验收结果不因此改变。问题只在报告事实记录。

## 2. 精确文件范围

只允许修改：

1. `docs/fixes/handoffs/HERMES_COMPLETION_3.md`

不得修改 `omnigent/`、`tests/`、r05 文档、已有任务卡或其他 handoff。

## 3. 失败证据与最小改法

### 3.1 已有失败证据

Codex 已在 Windows、Python 3.11.15、pytest 9.0.3，并把 `C:\Program Files\Git\usr\bin` 加入 `PATH` 以提供 `sh.exe` / `sleep.exe` 的环境复跑：

```text
25 failed, 45 passed, 42 warnings
HOST_FULL_EXIT=1
```

本轮直接使用这份已捕获证据纠正文档。Grok 不得运行 pytest、Ruff 或其他测试命令；若认为证据不足，只在报告中列出缺口并交回 Codex，由 Codex 决定是否让 Hermes 补跑。

### 3.2 最小改法

在 `HERMES_COMPLETION_3.md` 的“host 全套（含平台既有失败）”小节：

1. 把错误的 `exit 0` 改成实际捕获的退出码；当前可复现值为 `exit 1`。
2. 删除“pytest 不因既有失败返回非零”这一错误说明。
3. 明确写出捕获方式，例如 `$LASTEXITCODE` / `HOST_FULL_EXIT=1`。
4. 在末尾总结中同时写清 `loader exit 3`、`host exit 1`；两者均未冒充 GREEN。
5. 保留已有 25 个失败 nodeid、环境说明、三项 watcher GREEN、其余返工 diff 和证据。

不得修改源码来让 host Windows 全套变绿，不得删除失败 nodeid，也不得把 Windows 平台结果解释成 Gate 1。

## 4. 验证命令

完成报告纠正后只运行文档和工作树只读检查：

```powershell
rg -n -C 3 "host 全套|25 failed|HOST_FULL_EXIT|exit 1|loader exit 3|host exit 1|Gate 1|Gate 2" docs/fixes/handoffs/HERMES_COMPLETION_3.md
git diff --check -- docs/fixes/handoffs/HERMES_COMPLETION_3.md
git diff -- docs/fixes/handoffs/HERMES_COMPLETION_3.md
git status --short --branch
git rev-parse HEAD
git hash-object tests/runner/test_session_workspace_cache.py
```

保护值：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 阶段 1 测试 blob：`02cce3ca6e28233d5d0cac350a7be6316ff582d2`

本次是报告纠错；禁止重复运行 host 全套或任何已验证套件。若确需新测试证据，由 Hermes 另行执行，Grok 不代跑。

## 5. 禁止项

- 不得修改任何 `omnigent/` 源码、`tests/`、fixture、依赖、lockfile、CI 或 r05 文档。
- 不得运行 pytest、Ruff、构建、集成测试或 Gate 命令；只允许第 4 节的文档和 Git 只读检查。
- 不得修改或创建 `CODEX_TASK_4.md`、`GROK_REVIEW_4.md`，不得进入阶段 4。
- 不得 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean。
- 不得 commit/push/merge/tag、发版或编辑 PR/Issue。
- 不得声称阶段 3 已获 Grok approve、可 merge，或 Gate 1 / Gate 2 已执行、已判定、已通过。

## 6. 完成标准

仅当以下全部满足，Grok 才可把报告重新交给 Codex：

1. `HERMES_COMPLETION_3.md` 的 host 全套 summary 与真实退出码一致，不再出现“25 failed + exit 0”的矛盾。
2. 报告明确保留 host Windows 平台失败及 nodeid，不称全套 GREEN。
3. 报告末尾明确 `loader exit 3`、`host exit 1`；若实测数字变化，则以实际结果替换并解释环境差异。
4. 只有 `HERMES_COMPLETION_3.md` 被本轮修改，源码、测试、fixture、r05、既有任务卡均未触碰。
5. `git diff --check` 干净；HEAD 与阶段 1 blob 保护值不变。
6. 无 commit/push/merge/tag；Gate 1 / Gate 2 仍为未执行、未判定。

完成后只更新原交接报告 `docs/fixes/handoffs/HERMES_COMPLETION_3.md`，并回复 Codex 做不运行测试的只读复验。Codex 复验通过后，才可生成阶段 4 审查任务卡；若确需补测试，只能另交 Hermes。
