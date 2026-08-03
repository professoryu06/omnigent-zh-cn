# REVIEW_PACKAGE — core readiness (NO PUSH)

**生成时间：** 2026-07-24  
**用途：** 交给独立审查 agent / 人工审查。本包声明：**未 push、未 merge、未打新 Tag**。  
**工作副本：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**文档分支：** `docs/fix-plans-core-secondary` @ `dc83140` + **未提交** r04 文档改动  

---

## 1. 审查范围（本轮实际完成）

### 1.1 已完成并待审查

| ID | 内容 | 位置 | 证据 |
|----|------|------|------|
| R04 | Gate 脚本 P1：`EXIT:$?` → `PIPESTATUS[0]`；相对证据目录 → 绝对 `$EVIDENCE_ROOT` | PR#2 工作树未提交 diff | 见下方验收 |
| V3 | PR#3 #3016 定向测试复验 | worktree `tmp/omnigent-pr3` @ `744e3a0` | 2 passed |
| V4 | PR#4 #2747/#2746 定向测试复验 | worktree `tmp/omnigent-pr4` @ `30c04c3` | 7 passed |
| V5 | PR#5 #2853 Phase1 定向测试复验 | worktree `tmp/omnigent-pr5` @ `1f42a89` | 57 passed |

### 1.2 明确未完成（阻塞 / 后置）

| ID | 内容 | 原因 | 是否阻塞 merge |
|----|------|------|----------------|
| G1 | Linux 全仓 pytest Gate1 | WSL2 启动失败（HCS `0x800705aa`，内存紧张） | **是**（项目自定门槛） |
| G2 | AgentCenter C/E/R smoke | 同上 + 无可用 Linux 运行环境 | **是** |
| B5 | #2853 Phase2 真实 prompt apply | 计划内后续，本轮未做 | 否（Phase1 可单独合，但须注明 fail-loud only） |
| B6-B8 | #2539 / #2854 / #2967 | 未复现，禁止无证据实现 | 否（后置） |
| Scale | #3003/#3004/#2702/#3001 | 后置 | 否 |

---

## 2. 当前 PR 实时 head（审查前请再 `gh pr view`）

| PR | 分支 | head（本包生成时） | 技术状态 | 审查建议 |
|----|------|-------------------|----------|----------|
| #2 | `docs/fix-plans-core-secondary` | `dc83140` + **本地未提交 r04** | OPEN MERGEABLE | 审查 r04 diff 后可 commit；用户要求核心全完再 push |
| #3 | `fix/core-workspace-3016` | `744e3a0` | OPEN MERGEABLE | 代码 approve 候选；受 G1/G2 门槛阻塞 |
| #4 | `fix/core-spec-parse-2746-2747` | `30c04c3` | OPEN MERGEABLE | 同上 |
| #5 | `fix/core-2853-native-prompt` | `1f42a89` | OPEN MERGEABLE | **仅 Phase1 fail-loud**；不得写 prompt 已送达 |

---

## 3. 未提交 diff 清单（PR#2 工作树）

```
M  docs/fixes/PRE_MERGE_GATES.md
M  docs/fixes/STATUS.md
M  docs/fixes/POST_FIX_HANDOFF_PROMPT.md
?? docs/fixes/handoffs/HANDOFF_20260724_r04.md
?? docs/fixes/handoffs/QWEN_TASK_r04.md
?? docs/fixes/handoffs/REVIEW_PACKAGE_20260724_core.md
?? docs/fixes/handoffs/FINAL_FOR_REVIEWER_20260724.md
```

### PRE_MERGE_GATES 验收（已程序校验）

- `EXIT:$?` 裸捕获：**0**
- `artifacts/pre-merge` 相对路径：**0**
- `set -o pipefail`：**2**
- `PIPESTATUS[0]`：**2**
- `$EVIDENCE_ROOT`：已统一

关键模式：

```bash
set -o pipefail
uv run pytest -q ... 2>&1 | tee "$EVIDENCE_ROOT/baseline-pytest.txt"
pytest_status=${PIPESTATUS[0]}
echo "EXIT:$pytest_status" | tee -a "$EVIDENCE_ROOT/baseline-pytest.txt"
```

---

## 4. 定向测试证据（Windows，≠ Gate1）

环境：`F:\codex-ai\omnigent-zh-cn\.venv` Python 3.12.13 + pytest 9.0.3

| 套件 | 命令摘要 | 结果 | 日志 |
|------|----------|------|------|
| PR#3 | `pytest tests/runner/test_session_workspace_cache.py` | **2 passed / 2.89s** | `tmp/core-test-evidence/pr3.txt` |
| PR#4 | nested harness + codex model | **7 passed / 1.65s** | `tmp/core-test-evidence/pr4.txt` |
| PR#5 | native prompt delivery + claude/codex native | **57 passed / 2.74s** | `tmp/core-test-evidence/pr5.txt` |

路径：`F:\codex-ai\git项目部署\tmp\core-test-evidence\`

**禁止**把上述结果写成 Linux 全仓 Gate1 PASS。

---

## 5. 环境阻塞（诚实记录）

- WSL distros：`Ubuntu-24.04` / `docker-desktop` 均为 **Stopped**
- `wsl -d Ubuntu-24.04` 失败：`HCS/0x800705aa`（通常为资源不足）
- 本机可用内存约 **3.9 / 15.9 GB**
- 因此 **Gate1 / Gate2 无法在本机完成**；这是环境阻塞，不是代码未写

恢复建议：
1. 释放内存至 ≥8GB 空闲后 `wsl --shutdown` 再启动 Ubuntu-24.04
2. 或在独立 Linux CI/主机按 `PRE_MERGE_GATES.md` 跑 Gate1/Gate2
3. 证据写入 `$EVIDENCE_ROOT=/tmp/omnigent-premerge-evidence/<run-id>`

---

## 6. 核心完成度（审查用）

| 范围 | 进度 | 说明 |
|------|------|------|
| 门槛脚本正确性 | **完成** | r04 |
| 功能 PR 代码（#3016/#2747/#2746/#2853-P1） | **完成待合** | 已有 PR + 定向复验绿 |
| 合并门槛 G1/G2 | **0/2** | WSL 阻塞 |
| #2853 Phase2 apply | **0%** | 未做 |
| 未复现核心 #2539/#2854/#2967 | **0%** | 未做 |
| push / merge / 新 Tag | **未做** | 用户要求审查后再 push |

**结论：**  
“代码侧可审查的核心补丁”已就绪（#3/#4/#5 + PR#2 门槛脚本 r04）。  
“项目自定可合并门槛”**尚未达到**，因 Linux Gate 未跑。

---

## 7. 给审查 agent 的必做检查

```bash
# 1. 刷新 head
gh pr view 2 --json headRefOid,state,url,title
gh pr view 3 --json headRefOid,state,url,title
gh pr view 4 --json headRefOid,state,url,title
gh pr view 5 --json headRefOid,state,url,title

# 2. 审查 PR#2 工作树 r04
cd "F:/codex-ai/git项目部署/tmp/omnigent-review"
git status -sb
git diff -- docs/fixes/PRE_MERGE_GATES.md docs/fixes/STATUS.md docs/fixes/POST_FIX_HANDOFF_PROMPT.md

# 3. 可选复跑定向测试（Windows）
# 使用 omnigent-zh-cn .venv，PYTHONPATH 指向对应 worktree
```

审查输出请包含：
1. r04 是否可接受  
2. #3/#4/#5 是否仍 approve（注明门槛阻塞）  
3. 最多 3 条下一步（优先：恢复 WSL/Linux 跑 Gate，而非继续扩功能）

---

## 8. 用户决策记录

- **不 push**，等审查  
- 目标：核心修完再 push  
- 本包立场：可审查的核心代码/文档已齐；合并门槛因环境未齐，不得宣称可合

---

*fail-loud ≠ prompt 已送达。定向 67 ≠ Linux 全仓。未 push ≠ 未完成审查准备。*
