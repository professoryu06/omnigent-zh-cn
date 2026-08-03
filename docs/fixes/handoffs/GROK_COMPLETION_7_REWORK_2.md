# GROK COMPLETION 7 REWORK 2 — Gate 1 剩余全仓复跑

**执行者：** Grok（Gate 1 执行者，非独立审查者）  
**日期：** 2026-07-29  
**任务卡：** `docs/fixes/handoffs/CODEX_TASK_7_REWORK_2.md`  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`

---

## 1. 最终判定

### Gate 1 = **INVALID**

**原因（任务卡 §4.1 / §5）：** 复用身份核验阶段发现 **candidate 树路径上仍有遗留 host 子进程**，按卡必须停止全仓，**不得** broad `pkill`，不得继续 baseline/candidate 全仓 pytest。

因此：

- **未执行** baseline / candidate Linux 全仓 pytest（本轮无新 JUnit、无新 fail-ids、无新 new-failures）。
- **不得** 把旧 r2 空 `new-failures.txt` 或未完成全仓写成 PASS。
- **Gate 2：仍未执行、未判定。**
- **不代表可 merge**；无 commit/push/merge/tag。

---

## 2. RUN_ID 与证据路径

| 项 | 值 |
|----|-----|
| **RUN_ID** | `20260729-1143-dc83140-grok-r3` |
| **Linux evidence** | `/tmp/omnigent-premerge-evidence/20260729-1143-dc83140-grok-r3` |
| **Windows evidence** | `C:\Users\Administrator\gate1-evidence\20260729-1143-dc83140-grok-r3` |
| **旧 r2 证据（只读）** | `C:\Users\Administrator\gate1-evidence\20260729-0106-dc83140-r2` |
| **复用 baseline 树** | `/tmp/omnigent-gate1-baseline-20260729-0106-dc83140-r2` |
| **复用 candidate 树** | `/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2` |

未覆盖 r2 目录中任何文件。本轮仅写入新 `…-grok-r3` 证据目录 + 本报告。

双方证据目录内容在停止前已同步（setup 产物）：`run-id.txt`、`paths.txt`、`tree-heads.txt`、`reuse-identity.txt`、`candidate-status-reuse.txt`、`candidate-patch-reuse.patch`、`reconstructed-*`、`reused-evidence.sha256`、`candidate-protection-blobs-now.txt`、`pre-run-processes.txt`。

**本轮无** `baseline-junit.xml` / `candidate-junit.xml`（未开跑全仓）。

---

## 3. 复用身份核验结果

### 3.1 树 / venv / HEAD

| 检查 | 结果 |
|------|------|
| baseline `.venv` 存在 | **OK** |
| candidate `.venv` 存在 | **OK** |
| baseline HEAD | `81594243f7a17303b9ba477b938ac323f938c2e4` **OK** |
| candidate HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` **OK** |

### 3.2 status / patch / manifest / blob

| 检查 | 结果 |
|------|------|
| `candidate-status-reuse.txt` vs r2 `candidate-status.txt` | **cmp OK**（使用 `git status --short --branch`，与 r2 生成方式一致；任务卡写的仅 `--short` 会少 `## HEAD (no branch)` 行，已在证据中记录） |
| `candidate-patch-reuse.patch` vs r2 `reconstructed-candidate.patch` | **cmp OK**（68561 bytes） |
| reconstructed tracked/untracked files vs r2 | **cmp OK** |
| reconstructed untracked blobs vs r2 | **cmp OK** |
| 同上 vs Windows `candidate-tracked-files.txt` / `candidate-untracked-files.txt` / `candidate-untracked-blobs.txt` | **cmp OK** |

### 3.3 保护 blob（candidate 树）

| 文件 | blob | 期望 |
|------|------|------|
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | ✅ |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` | ✅ |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | ✅ |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` | ✅ |

### 3.4 复用 r2 既有正面证据 receipt（只读 SHA-256）

写入 `reused-evidence.sha256`，覆盖：

- `candidate-status.txt`
- `reconstructed-candidate.patch`
- `targeted-current.txt`（r2 定向 **136 passed**，本轮**未重跑**）
- `ruff.txt`（本轮**未重跑**）
- `diff-check-tracked.txt` / `diff-check-untracked.txt`（本轮**未重跑**）
- `candidate-protection-blobs.txt`

### 3.5 预跑进程检查 — **失败 → INVALID**

`pre-run-processes.txt` 内容：

```text
adminis+   45236   30064  0 10:59 ?        00:00:02 /tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2/.venv/bin/python -m omnigent.host._daemon_entry --local
adminis+   45237   45236  0 10:59 ?        00:00:05 /tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2/.venv/bin/python -m omnigent.cli server --host 127.0.0.1 --port 6767 --database-uri sqlite:////home/administrator/.omnigent/chat.db --artifact-location /home/administrator/.omnigent/artifacts
```

路径命中复用 candidate 树；属 **host/server 子进程**。任务卡要求：存在仍在运行的旧 pytest/runner/**host** 子进程时 **停止本轮并判 INVALID**，且 **不得** broad `pkill`。

**本执行者遵守：未杀进程、未开跑全仓。**

---

## 4. 对旧报告不可审计点的纠正（事实保留）

即使本轮 INVALID，仍记录任务卡要求的纠正，避免沿用错误推断：

| 旧表述风险 | 纠正 |
|------------|------|
| `timeout=300` 被当成全套总时限 | **每测试 wallclock 上限 300s**，不是 15k+ 用例总时限 |
| `timeout_method=thread` 导致无 JUnit | 单测超时会整进程退出；不证明“全套总时间超限” |
| 候选约 `15162 / 3–4%` | 旧候选日志实为约 **15242 items**，进度至少到约 **57%**（以 r2 日志为准，本轮未重跑全仓） |
| 空 `new-failures.txt` = 0 新增失败 | 仅表示 **无可比较完整失败集**，不能作为相对 PASS |
| 旧 baseline 文本被覆盖到只剩 structlog 一行 | 旧 baseline 与 candidate **不能**声称同一 nodeid 超时 |

---

## 5. 本轮未执行的全仓命令（设计意图，因 INVALID 未跑）

若进程检查通过，将 **顺序**（禁止并行）执行：

```bash
# 每测试 300s，timeout_method=signal（CLI 覆盖；非默认 thread）
# 禁止 -p no:timeout；禁止提高 300s 上限
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=60s 21600s \
  uv run pytest -q --color=no \
    --timeout=300 --timeout-method=signal \
    --junitxml="$LINUX_EVIDENCE_ROOT/${label}-junit.xml" 2>&1 | tee "$log"
```

先 baseline，后 candidate。  
**实际：** 因 §3.5，**两条全仓均未启动**。

因此无：

- `baseline-pytest.exit` / `candidate-pytest.exit`（本轮）
- 本轮 JUnit parse
- 本轮 `baseline-fail-ids.txt` / `candidate-fail-ids.txt` / `new-failures.txt`
- 本轮 `baseline-known-failures.md`

不得引用 r2 空 fail 列表冒充本轮结果。

---

## 6. timeout 模式声明

- 计划模式：`--timeout=300 --timeout-method=signal`（保留 300s 单测上限，使超时成为 case 级失败并允许 session 继续写 JUnit）。
- **未使用** `-p no:timeout`。
- **未提高** 300 秒上限。
- **未** 将上述描述为默认 `thread` 模式已通过（因未跑全仓）。

---

## 7. 旧定向 / Ruff / diff-check / 保护（仅 receipt 引用）

在复用 receipt（`reused-evidence.sha256`）与树身份匹配的前提下，**仅引用 r2 既有证据，本轮未重跑**：

| 证据 | 处理 |
|------|------|
| 定向 136 passed | 只读引用 r2 `targeted-current.txt` |
| Ruff clean | 只读引用 r2 `ruff.txt` |
| tracked/untracked diff-check | 只读引用 r2 对应文件 |
| 四保护 blob | candidate 树现算与期望一致 |

这些 **不等于** 全仓 GREEN，也 **不能** 单独构成 Gate 1 PASS。

---

## 8. 源工作树保护（运行后）

| 项 | 结果 |
|----|------|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| workspace blob | `02cce3ca…` |
| model blob | `be43ec45…` |
| idle blob | `58b24b7d…` |
| serve blob | `61162180…` |
| 源码/tests/config/lockfile | **未由本轮修改** |
| 本轮源树唯一允许新增 | `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_2.md` |
| 既有 handoff | **未改**（含 `HERMES_COMPLETION_7_REWORK.md`） |

---

## 9. 判定对照 §5

| 规则 | 是否满足 |
|------|----------|
| PASS（绝对） | **否** — 无 candidate 全仓 exit 0 / 本轮 JUnit |
| PASS（相对 main） | **否** — 无完整 baseline/candidate 失败集与有效 JUnit |
| FAIL | **否** — 未跑出 candidate 相对 baseline 的新增 case 失败证据 |
| **INVALID** | **是** — 复用前遗留 host 进程；全仓未完成；无本轮可审计失败集 |

---

## 10. 建议 Codex 后续（Grok 不执行）

1. **人工/编排者**在确认无其他 WSL 关键负载后，**定向**结束仅绑定  
   `/tmp/omnigent-gate1-candidate-20260729-0106-dc83140-r2` 的 host/server PID（45236/45237 以现场 `ps` 为准），或重建干净 candidate 树。  
2. Grok **不得**自行 `pkill`。  
3. 进程清空且树身份仍匹配后，另开任务卡重跑 **仅** baseline→candidate 全仓（仍 `--timeout=300 --timeout-method=signal`）。  
4. 仍禁止拼接 r2 未完成全仓与本轮证据。

---

## 11. 禁止项遵守

- [x] 未改 `omnigent/`、`tests/`、`pyproject.toml`、`uv.lock`、r05、既有 handoff  
- [x] 未用 `-p no:timeout`，未提高 300s  
- [x] 未重跑定向 / Ruff / diff-check / Gate 2  
- [x] 未覆盖 r2 证据  
- [x] 未 checkout/switch/fetch/rebase/cherry-pick/stash/reset/clean  
- [x] 未 commit/push/merge/tag  
- [x] 未签发 merge 许可  

---

## 12. 最终 git status（源工作树摘要）

```text
## docs/fix-plans-core-secondary...origin/docs/fix-plans-core-secondary
 M docs/fixes/... (r05 既有)
 M omnigent/... / tests/... (阶段累积既有 dirty)
?? docs/fixes/handoffs/   # 含本报告 GROK_COMPLETION_7_REWORK_2.md
?? omnigent/inner/native_prompt_delivery.py
?? tests/... (阶段累积 untracked)
```

本轮 **仅新增** `docs/fixes/handoffs/GROK_COMPLETION_7_REWORK_2.md` 作为源树交付物。

---

**交回 Codex 只读验收。**  
**Gate 1 = INVALID。** Gate 2 未执行、未判定；不可 merge。
