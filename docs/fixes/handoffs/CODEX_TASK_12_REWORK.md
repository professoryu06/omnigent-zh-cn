# CODEX TASK 12 REWORK — r3工作树Codex home精确清理与报告补正

> **执行者：** Grok（清理返工执行者；不重跑Gate）  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **唯一仓库交付：** `docs/fixes/handoffs/GROK_COMPLETION_12_REWORK.md`

**目标：** 精确清理Gate 2 r3在工作树忽略目录内遗留的、可唯一归属本RUN的临时Codex home，并用新报告补正原`leftover=0`的范围；r3结论永久保持`INVALID`。

**当前状态：** Gate 1=`PASS（相对 main）`、非全仓GREEN；Gate 2 r3=`INVALID`；历史正式业务FAIL仍为0202；不可merge。

---

## 1. 已确认缺口

r3正式RUN：

`20260730-1235-dc83140-grok-gate2-r3`

正式evidence：

`C:\Users\Administrator\gate2-evidence\20260730-1235-dc83140-grok-gate2-r3\`

Codex只读验收确认：

- r3的`INVALID`四态判定正确；
- `$RUNTIME_ROOT`已删除、相关PID已死亡、64774端口已释放；
- 但C执行窗口内在工作树新建并遗留：

`F:\codex-ai\git项目部署\tmp\omnigent-review\.codex-tmp\omnigent-codex-home-qun0egm8\`

只读元数据：

- 目录创建时间UTC：`2026-07-30T04:36:39`，位于C执行窗口；
- 共17个后代项；
- 15个reparse point，其中包含`auth.json`符号链接和skill目录链接；
- 1个普通文件`config.toml`；
- 1个普通子目录`skills`；
- Git忽略`.codex-tmp/`，所以普通`git status`看不到该残留。

原`GROK_COMPLETION_12.md`声称“仓库内仅新建完成报告”，且`cleanup.txt`写`leftover_after=0`，但未披露该工作树临时目录。旧报告和旧evidence不得改写；本返工用新报告补正。

## 2. 必读

1. `docs/fixes/handoffs/CODEX_TASK_12_REWORK.md`
2. `docs/fixes/handoffs/CODEX_TASK_12.md`
3. `docs/fixes/handoffs/GROK_COMPLETION_12.md`
4. r3 evidence中的`cleanup.txt`、`runtime-sha256-manifest.txt`、`FINAL.txt`、`leak-scan.txt`
5. `.gitignore`中`.codex-tmp/`规则
6. `omnigent/inner/codex_executor.py`中临时`omnigent-codex-home-*`创建逻辑（只读）

不得读取`auth.json`链接目标或`config.toml`内容；只允许读取文件系统元数据、链接类型、叶名、数量、时间和路径。

## 3. 固定身份

开始和结束均记录：

- HEAD：`dc83140c73ceb12fa165753c1880c19f68da86f4`
- 阶段 10四blob：
  - `5bf5e587b9177a9ecbce572b11656edac31ea7fe`
  - `0375e5f951d82c01c9f67e8cf7b41a90aff10330`
  - `63291bfa4bc47c196e04a218c82b782ecb613786`
  - `4cae0f53cb724c991a1c502c2919e37da7b7737a`
- 四保护blob：
  - `02cce3ca6e28233d5d0cac350a7be6316ff582d2`
  - `be43ec45816e8ece4192822506df8072580910e0`
  - `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8`
  - `6116218097f2352c467524fd0ddf0838315aa524`
- `git status --short --branch`

任一不匹配则停止，报告`INVALID_REWORK_IDENTITY`；不得修树、checkout或回滚。

## 4. 外部清理证据

新建独立外部证据目录：

`C:\Users\Administrator\gate2-evidence\cleanup-r3-codex-home-<timestamp>\`

只能保存：

- `before-metadata.txt`
- `process-check.txt`
- `path-safety.txt`
- `remove-actions.txt`
- `after-metadata.txt`
- `CLEANUP_SUMMARY.txt`

不得复制、hash、打开或扫描`auth.json`链接目标和`config.toml`内容。不得把credential值、config正文或role prompt写入清理证据。

## 5. 路径与归属安全检查

固定路径：

```powershell
$WORKTREE = (Resolve-Path -LiteralPath 'F:\codex-ai\git项目部署\tmp\omnigent-review').Path
$CODEX_TMP = Join-Path $WORKTREE '.codex-tmp'
$TARGET = Join-Path $CODEX_TMP 'omnigent-codex-home-qun0egm8'
```

删除前必须全部满足并记录：

1. `$WORKTREE`精确等于任务卡工作树。
2. `$CODEX_TMP`的绝对父级精确为`$WORKTREE`。
3. `$TARGET`的绝对父级精确为`$CODEX_TMP`。
4. `$TARGET`叶名精确等于`omnigent-codex-home-qun0egm8`；不得使用通配符。
5. `$TARGET`存在且自身是普通目录，不是reparse point。
6. 创建时间UTC为`2026-07-30T04:36:39`所在秒；若不匹配，停止。
7. 后代项总数=17、reparse point数=15、普通文件数=1；普通文件叶名只能是`config.toml`。
8. 普通子目录只能是`skills`。
9. `auth.json`必须是reparse point；只记录`LinkType=SymbolicLink`，不得读取或打印Target。
10. 所有其它叶项必须位于`skills`下且为reparse point；不得跟随链接。
11. 当前无进程命令行包含目标绝对路径或叶名。
12. r3 PID `2820/21420/40232/40612`均已死亡，64774无监听。

任一条件不满足，停止并写`CLEANUP_SUMMARY.txt`为`CLEANUP_NOT_PERFORMED`；不得扩大范围或猜测删除。

## 6. 精确删除方法

禁止递归删除整个`.codex-tmp`，禁止通配符，禁止跨shell拼接删除列表。

在同一PowerShell进程内，按以下顺序使用`Remove-Item -LiteralPath`：

1. 枚举`$TARGET\skills`下的每个**已验证reparse point**，逐个删除链接本身；不得跟随或删除链接目标。
2. 删除已验证为符号链接的`$TARGET\auth.json`链接本身；不得触碰链接目标。
3. 删除普通文件`$TARGET\config.toml`；不得读取内容。
4. 确认`$TARGET\skills`为空后，以非递归方式删除该目录。
5. 确认`$TARGET`为空后，以非递归方式删除该目录。
6. 不得删除`.codex-tmp`父目录；其中其它内容均不在本卡范围。

每一步记录叶路径、类型、成功/失败和时间；不得记录链接Target或文件内容。

若任一步失败，停止；不得改用`Remove-Item -Recurse $CODEX_TMP`、`cmd /c rmdir`、Python删除、`git clean`或其它扩大范围的手段。

## 7. 删除后验证

必须确认并记录：

- 精确`$TARGET`不存在；
- `.codex-tmp`父目录仍存在，不属于本RUN的其它项未被触碰；
- r3四个PID仍dead；
- 64774仍无listener；
- 无命令行包含r3 RUN_ID、64774、目标路径或目标叶名的非shell进程；
- r3旧evidence所有文件的mtime保持不变；
- 0202和其它旧evidence未修改；
- Git tracked/untracked状态除新返工报告外与开始一致；忽略项中精确目标已消失。

`CLEANUP_SUMMARY.txt`只有全部满足才写：

```text
CLEANUP_OK=true
target_removed=true
parent_preserved=true
credential_target_untouched=true
run_process_matches=0
port_64774_listeners=0
old_evidence_unchanged=true
```

其中`credential_target_untouched=true`只能通过“仅删除符号链接本身且未跟随”来判定；不得打开credential文件验证。

## 8. r3结论与报告边界

r3永久保持：

- `Gate 2 = INVALID`
- C timeout=true
- cli_exit=-1、不可信
- session_id=UNKNOWN
- 0202旧400未见但未证明消除
- 后五轮未执行

本返工不能：

- 改写`GROK_COMPLETION_12.md`；
- 改写r3的`cleanup.txt`、`FINAL.txt`、leak-scan或其它evidence；
- 把事后清理拼回r3并提升为FAIL/PASS；
- 启动server/host/runner或第二个Gate RUN。

新报告必须明确：

- 原`leftover_after=0`只覆盖r3驱动枚举的进程/RUNTIME_ROOT，不足以证明工作树无忽略运行残留；
- r3 evidence leak-scan只覆盖该evidence根，不覆盖工作树`.codex-tmp`；
- 事后清理只恢复工作树卫生，不改变r3的INVALID状态。

## 9. 唯一报告

只新建：

`docs/fixes/handoffs/GROK_COMPLETION_12_REWORK.md`

报告必须包含：

1. `REWORK_CLEANUP_OK`或`REWORK_CLEANUP_FAILED`唯一结论。
2. 外部清理证据路径。
3. 删除前路径归属、创建时间、数量和reparse类型摘要。
4. 精确删除步骤与结果；不含链接Target或任何文件内容。
5. 删除后目标不存在、父目录保留、PID/端口/进程匹配为0。
6. r3/0202旧evidence未修改的mtime核对。
7. HEAD、阶段 10四blob、四保护blob和git status核对。
8. 明确r3仍为INVALID、Gate 2非PASS、不可merge。
9. 下一次Gate 2新RUN必须在开始/结束快照`.codex-tmp`，并在finally精确清理本RUN新建的`omnigent-codex-home-*`。

## 10. 禁止项

- 不得读取、复制、hash或打印`auth.json`链接目标、credential值、config正文或prompt正文。
- 不得删除`.codex-tmp`父目录或任何非精确目标。
- 不得使用通配符、递归删除父目录、批量kill、`git clean`或跨shell删除。
- 不得修改源码、tests、policy、STATUS、POST_FIX、旧handoff或任何旧evidence。
- 不得运行pytest、Ruff、Gate 1、Gate 2、server、host、runner或真实CLI。
- 不得commit/push/merge/tag、发版或编辑PR/Issue。
- 不得把清理成功写成Gate 2 PASS或merge许可。

## 11. 完成标准

1. 删除前12项安全检查全部满足。
2. 只删除精确`omnigent-codex-home-qun0egm8`及其自身链接/普通config，不跟随任何reparse target。
3. 目标消失、`.codex-tmp`父目录保留、非目标项未触碰。
4. r3相关PID dead、64774 free、进程匹配为0。
5. r3/0202旧evidence和仓库旧文件未修改。
6. 只新增`GROK_COMPLETION_12_REWORK.md`。
7. r3仍为INVALID；Gate 2仍非PASS；不可merge。
8. 无commit/push/merge/tag。

完成后停止，交回Codex只读验收。不得自行开始下一个Gate 2 RUN。
