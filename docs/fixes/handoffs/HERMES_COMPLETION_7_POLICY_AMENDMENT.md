# HERMES_COMPLETION_7_POLICY_AMENDMENT — Gate 1 政策修订落地

**执行者：** Hermes（政策文档执行者）
**批准者：** Codex（2026-07-29）
**日期：** 2026-07-29
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 修改的文件

仅修改：`docs/fixes/PRE_MERGE_GATES.md`（§1.2 相对 PASS 行替换 + 新增安全条件 + 政策修订记录）

仅新建：`docs/fixes/handoffs/HERMES_COMPLETION_7_POLICY_AMENDMENT.md`（本文件）

---

## 2. 精确 diff 摘要

§1.2 表格第二行替换：

- **旧**：`clean main 已有失败，且集成树失败 nodeid ⊆ main 失败集（同环境、同依赖）` → 标注「已知环境/已知 flaky」
- **新**：`clean main 已有失败，且候选树失败 nodeid ⊆ main 失败集（同环境、同依赖、同隔离状态）` → 必须同时满足"相对 PASS 安全条件"

新增内容（紧接表格后）：

- `#### 相对 PASS 安全条件`（九条）
- `> 政策修订记录（2026-07-29，Codex显式批准）`

---

## 3. 九条安全条件逐项核对

| # | 条件 | 落地 |
|---|---|---|
| 1 | 同 OS/依赖/隔离 + 双侧 JUnit + 退出码冻结 | ✅ 第 1 条 |
| 2 | candidate-only 失败为零 | ✅ 第 2 条 |
| 3 | 三类逐项分类（known_environment / known_flaky / documented_main_code_failure），不得混称 | ✅ 第 3、7 条 |
| 4 | 归一化语义指纹相同，保留异常类型/实际期望值/HTTP 状态/模块名/策略动作 | ✅ 第 4 条 |
| 5 | 语义变化必须独立审查 | ✅ 第 5 条 |
| 6 | 新增测试全通过 + 定向/Ruff/diff-check/保护证据有效 | ✅ 第 6 条 |
| 7 | 三类分别统计，不得混称 | ✅ 第 7 条 |
| 8 | documented main baseline 必须显式批准 | ✅ 第 8 条 |
| 9 | 相对 PASS ≠ 全仓 GREEN ≠ Gate 2 ≠ 可 merge | ✅ 第 9 条 |

---

## 4. 文档验证命令结果

### git diff --check

```
DIFF_CHECK_EXIT=0
```

无空白错误。✅

### grep 关键短语

```
207: candidate-only failure/error 均为 Gate 1 FAIL
211: documented_main_code_failure
212: 归一化语义指纹
215: 不得把documented_main_code_failure称为环境或flaky
216: 显式.*批准
217: 不等于全仓GREEN，不等于Gate 2 PASS，不等于可merge
219: 政策修订记录（2026-07-29，Codex显式批准）
```

全部关键短语可检索。✅

---

## 5. 编辑前后身份核对

### HEAD

| 时机 | 值 |
|---|---|
| 编辑前 | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| 编辑后 | `dc83140c73ceb12fa165753c1880c19f68da86f4` |

### 四保护 blob

| 文件 | 编辑前 | 编辑后 | 状态 |
|---|---|---|---|
| workspace | `02cce3ca...` | `02cce3ca...` | ✅ |
| model | `be43ec45...` | `be43ec45...` | ✅ |
| idle | `58b24b7d...` | `58b24b7d...` | ✅ |
| serve | `61162180...` | `61162180...` | ✅ |

### STATUS.md SHA-256

| 时机 | 值 |
|---|---|
| 编辑前 | `702fed996113c8dde12a586f02b510c59c5deab9cbe73dff3d6b8080924d2def` |
| 编辑后 | `702fed996113c8dde12a586f02b510c59c5deab9cbe73dff3d6b8080924d2def` |

### POST_FIX_HANDOFF_PROMPT.md SHA-256

| 时机 | 值 |
|---|---|
| 编辑前 | `a569df285568059d592cb508ac582908ed8736814021b7fe72465f1f826214fb` |
| 编辑后 | `a569df285568059d592cb508ac582908ed8736814021b7fe72465f1f826214fb` |

### 旧 handoff 文件

编辑前后 SHA-256 均一致（38 个文件，完整清单见编辑前终端输出）。除 `PRE_MERGE_GATES.md` 和本报告外零修改。

---

## 6. 未执行声明

- 未运行 pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器 E2E 或真实 CLI smoke。
- 未启动/终止 WSL 进程，未清理 tmux/host/server。
- 未修改 STATUS、POST_FIX、旧 handoff、源码/tests/config/lockfile/CI 或 evidence。
- 未把 Gate 1 写成 PASS。
- 未 stage/commit/push/merge/tag、发版或编辑 PR/Issue。

---

## 7. Gate 状态

- **本轮只落地政策修订。**
- **Gate 1 仍待 Codex 只读验收**（验收 r6 证据是否满足新九条安全条件）。
- **Gate 2 未执行、未判定。**
- **不可 merge。**

---

## 8. 禁止项遵守声明

- 未修改 STATUS 或把 Gate 1 写成 PASS。
- 未修改 POST_FIX、旧 handoff、源码/tests/config/lockfile/CI 或 evidence。
- 未删减 §4 任何安全条件。
- 未运行 pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器 E2E 或真实 CLI smoke。
- 未启动/终止 WSL 进程或清理 tmux/host/server。
- 未 stage/commit/push/merge/tag、发版或编辑 PR/Issue。
- 未宣称全仓 GREEN、Gate 2 PASS 或可 merge。
