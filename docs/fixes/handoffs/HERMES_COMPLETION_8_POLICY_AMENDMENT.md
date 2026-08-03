# HERMES_COMPLETION_8_POLICY_AMENDMENT — Gate 2 Phase 2 正向/负向分轨 + Gate 1 快照更新

**执行者：** Hermes（文档执行者）
**日期：** 2026-07-29
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 修改的文件

仅修改：`docs/fixes/PRE_MERGE_GATES.md`

- Gate 2 §2.1：单一 Executor 拆为五轮次（C / E-pos / E-pos-strict / E-neg-warn+E-neg-strict / R）
- Gate 2 §2.2：启动模板重写（独立 evidence root、preflight、六轮次顺序、进程清理约束）
- Gate 2 §2.3：断言表替换为 AC-1～AC-6（含 AC-4-pos/AC-4-neg/AC-5-pos/AC-5-neg）+ 四态判定规则
- 执行快照：Gate 1 更新为 PASS（相对 main），Gate 2 仍为未执行/未判定

仅新建：`docs/fixes/handoffs/HERMES_COMPLETION_8_POLICY_AMENDMENT.md`（本文件）

---

## 2. 关键政策要点落地核对

| 要求 | 落地 |
|---|---|
| 正向 codex Phase 2 与负向 warn-only native 分轨 | ✅ 五轮次表 + 独立 session |
| 禁止 receipt-mismatch/resume/fork codex-native 充当 E-negative | ✅ 第 259 行明确禁止 |
| E-pos-strict 必须新 fresh 非 fork session/runner，进程启动前 STRICT=1 | ✅ 第 255 行 + 第 330-333 行 |
| 第二个 warn-only native 缺失 → NOT_EXECUTED | ✅ 第 306 行 + 第 372 行 |
| Gate 1 更新为 PASS（相对 main），非全仓 GREEN | ✅ 第 383 行 |
| Gate 2 仍未执行、未判定 | ✅ 第 384 行 |
| 不可 merge | ✅ 第 385 行 |
| AC-1～AC-6 完整 | ✅ 第 360-367 行 |
| PASS/FAIL/INVALID/NOT_EXECUTED 四态判定 | ✅ 第 370-374 行 |
| prompt 正文/credential 不得出现在证据中 | ✅ 第 308、354、364 行 |

---

## 3. 文档验证结果

### grep 关键短语（三组）

全部关键短语可检索：E-positive、E-negative、AC-4-pos/neg、AC-5-pos/neg、Phase 2、NOT_EXECUTED、INVALID、PASS（相对 main）、126/126、candidate-only、r6 证据根、Gate 2 未执行、不可 merge、receipt-mismatch、resume、fork、进程启动前、第二个 native、prompt 正文、credential。✅

### git diff --check

```
DIFF_CHECK_EXIT=0
```

✅

### HEAD + 四保护 blob

| 项 | 值 | 状态 |
|---|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` | ✅ |
| workspace | `02cce3ca...` | ✅ |
| model | `be43ec45...` | ✅ |
| idle | `58b24b7d...` | ✅ |
| serve | `61162180...` | ✅ |

---

## 4. 未执行声明

- 未运行 pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器 E2E 或真实 CLI。
- 未启动/终止 WSL 进程，未清理 tmux/host/server。
- 未修改 STATUS、POST_FIX、旧 handoff、源码/tests/config/lockfile/CI 或 evidence。
- 未改变 Gate 1 九条安全条件或批准记录。
- 未读取/复制/打印 credential/token 或 prompt 正文。
- 未 stage/commit/push/merge/tag、发版或编辑 PR/Issue。
- 未声称 Gate 2 PASS、全仓 GREEN 或可 merge。

---

## 5. Gate 状态

- **本轮只落地 Gate 2 政策分轨 + Gate 1 快照更新。**
- **Gate 1 = PASS（相对 main），不等于全仓 GREEN。**
- **Gate 2 未执行、未判定。**
- **不可 merge。**

---

## 6. 禁止项遵守声明

- 未修改 `omnigent/`、`tests/`、STATUS、POST_FIX、配置、依赖、lockfile、CI、旧 handoff 或 evidence。
- 未改变 Gate 1 九条安全条件、批准记录或 r6 evidence。
- 未运行 pytest、Ruff、Gate 1/2、AgentCenter、浏览器、Omnigent/Codex/Claude 等真实 CLI。
- 未启动、终止或清理 host/server/runner/tmux。
- 未读取、复制、打印 credential/token 或 prompt 正文。
- 未 stage/commit/push/merge/tag、发版或编辑 PR/Issue。
- 未声称 Gate 2 PASS、全仓 GREEN 或可 merge。
