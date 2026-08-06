# 修完后交给审查 agent 的标准提示词（模板 + 当前填充）

**用法：** 每轮结束后更新「当前快照」，复制文末「完整提示词」。  
**约束：** 不 merge、不打新 Tag、不关上游 issue、不实现未复现问题（除非另授）。  
**时间快照：** 状态须 `gh` 重查。

**合并前门槛规格（命令/环境/证据/pass-fail）：**  
→ **[PRE_MERGE_GATES.md](./PRE_MERGE_GATES.md)**（必读）

---

## 当前快照（约 2026-07-23）

| PR | 主题 | 状态 |
|----|------|------|
| [#2](https://github.com/professoryu06/omnigent-zh-cn/pull/2) | 文档/门槛规格 | OPEN — 以 `gh pr view 2` 为准 |
| [#3](https://github.com/professoryu06/omnigent-zh-cn/pull/3) | #3016 | OPEN 未 merge；代码可合 **但受门槛阻塞** |
| [#4](https://github.com/professoryu06/omnigent-zh-cn/pull/4) | #2747/#2746 | OPEN 未 merge；同上 |
| [#5](https://github.com/professoryu06/omnigent-zh-cn/pull/5) | #2853 Phase1 fail-loud | OPEN 未 merge；**mitigated 非送达** |

### 验证与门槛（严禁夸大）

| 项 | 状态 |
|----|------|
| 定向 67 tests + 目标 Ruff | **已通过**（临时 main+#3+#4+#5）— **≠ 全仓通过** |
| Gate 1 Linux 全仓 | **未执行 → 门槛未达标**（需 Ubuntu 22.04/24.04 + Python 3.12 + `uv sync --locked --extra dev`；见 PRE_MERGE_GATES） |
| Gate 2 AgentCenter smoke | **未执行 → 门槛未达标** |
| #2853 | **Phase1 单元级 fail-loud 完成**；**真实送达未实现**；**实机 E2E 未验证** |
| Tag | 已有 `v0.6.0-zhcn.1`；本轮**未创建新 Tag** |
| **是否达到合并门槛** | **否** |

### 建议顺序

1. 按 PRE_MERGE_GATES 在 **Linux** 跑 clean main 与 integrate 全仓 pytest  
2. AgentCenter 最小 C/E/R smoke（断言见该文档）  
3. 维护者 merge #3 → #4 → #5  
4. 刷新 STATUS 后 merge #2  
5. 可选发版  
6. #2853 Phase2 → #2539 → #2854 → #2967 → Scale  

### 上游快照（须重查）

- #3013：open draft  
- #2833：open、未 merge、不默认落地  

---

## TodoList（摘要）

**A 门槛：** [ ] Linux 全仓（绝对全绿 **或** 相对 main 无新增失败） [ ] AgentCenter smoke  
**A 合并：** [ ] #3 [ ] #4 [ ] #5 [ ] #2  
**B 后续：** Phase2 apply；#2539/#2854/#2967  
**C 上游：** #3013/#2833 仅跟踪  
**D Scale：** 后置  

---

## 完整提示词（复制给 Codex）

```text
审查 Omnigent-zh-cn 合并前门槛是否写清、是否已达标。

仓库：https://github.com/professoryu06/omnigent-zh-cn
必读：docs/fixes/PRE_MERGE_GATES.md 、POST_FIX_HANDOFF_PROMPT.md 、STATUS.md
先：gh pr view 2/3/4/5 ；git ls-remote --tags origin

事实：
- #3/#4/#5 定向 67+Ruff 曾绿；均 OPEN 未 merge
- #2853=Phase1 fail-loud only；送达/E2E 未做
- Gate1 Linux 全仓、Gate2 AgentCenter smoke：文档已写可复跑步骤；执行记录为未执行则门槛未达到
- Tag 已有 v0.6.0-zhcn.1；本轮无新 Tag
- 禁止把 67 tests 写成全仓通过；禁止 fail-loud=prompt 已送达

输出：门槛是否达标、文档缺口、最多 3 条下一步。不 merge、不打 Tag、不做 Phase2。
```
