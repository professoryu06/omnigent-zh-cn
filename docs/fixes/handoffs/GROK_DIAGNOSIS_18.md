# GROK DIAGNOSIS 18 — CLI 0.146.0 单次 Omnigent C / D2

> **角色：** Grok（只读诊断执行者）  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_18.md`  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **唯一仓库交付：** 本文件  
> **完成动作：** 交回 Codex 只读验收；未 commit/push/merge/tag  

---

## 1. RUN / 路径 / 端口 / 时间窗

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-190615-dc83140-grok-d2-c-cli0146-r1` |
| **Evidence（持久保留）** | `C:\Users\Administrator\omnigent-diagnostics\20260730-190615-dc83140-grok-d2-c-cli0146-r1` |
| **Runtime** | `%TEMP%\omnigent-d2-c-cli0146-20260730-190615-dc83140-grok-d2-c-cli0146-r1`（**已删除**） |
| **SERVER_PORT** | `55518` |
| **SERVER_URL** | `http://127.0.0.1:55518` |
| **时间窗（UTC 约）** | 11:06:15 setup → server READY+10s → host online → C 11:06:40–11:06:44 → finally/leak ~11:06:51 |
| **报告时 evidence 根存在** | **True**（48 文件，含 `leak-scan.txt`） |

未拼接阶段 14–17 / Gate2 r4 / 失效 Task 16 的 PID、thread、exit 或 evidence 正文。  
同会话早期曾有若干**未完成协议**的试跑 RUN（server/host 就绪失败或 C 参数/agent 形态错误），均使用独立 RUN_ID；**本报告唯一完整走完 required-check → diagnosis → final-check → manifest → leak-scan 的 RUN 为上表。**

---

## 2. 唯一分类（evidence 冻结值）

```text
primary_classification=DIAG_RUNNER_SPAWN
subcase=RUNNER_NOT_SPAWNED
```

| 字段 | 值 |
|---|---|
| `business_success` | False |
| `product_idle_watchdog_s` | 240（未修改） |
| `full_gate2_executed` | **False** |
| `attempt` | `1_of_1` |

### 审计保留意见（供 Codex RO）

冻结分类来自本 RUN 的 `DIAGNOSIS.txt` / `d2-outcome.txt`。下列事实使 **spawn 窗口观测可信度不足**，RO 可改判 `DIAG_INCONCLUSIVE` 而不与本交付冲突：

1. **约 1s live samples 实际为空**（`sample_count=0`；`d2-samples-live-sanitized.jsonl` 仅占位字节；observer stderr 有错误痕迹，runtime 删除前 stream hash 记录 `observer.stderr.log` size=546）。  
2. **外层 wait 在 ~4s 标记 `outer_budget_timeout`**（`c_duration_ms=4006`），与声明的 300s 外层预算不一致；`c_exit` 为空。业务 exit 时间线**不可作为 idle 240s 终态**。  
3. C stderr（脱敏）显示失败于 **turn setup / agent 包**：`config.yaml missing required field: spec_version`（本地 runtime agent 声明 `spec_version: 1`，但远端/runner 侧解析仍报缺失）——失败点在 **runner/codex spawn 之前的 agent 规格装配**，并非已 spawn 后的 stall/relay。  

**本卡仍按冻结文件汇报 `DIAG_RUNNER_SPAWN`；不在 final-check 后改写 evidence。**

**不是** Gate 2 PASS；**不是** `DIAG_TRANSIENT_R4`；**不可 merge**。

---

## 3. Identity / 八 blob / native / TUN

| 检查 | 结果 |
|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` start=end |
| branch | `docs/fix-plans-core-secondary` |
| 八候选 blob（工作树 `git hash-object`） | start/end `all_match=True`（与任务卡期望一致） |
| 预检 residual | `count=0` / `pass=True`（self/ancestor 已标记） |
| `.codex-tmp` | start 空；end `sets_equal=True` |
| native path | 任务卡固定 npm vendor `...\bin\codex.exe` |
| version / size / SHA | **codex-cli 0.146.0** / **358650672** / `bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb` start=end，`shim=False` |
| TUN | 强制数组；`meta_up_at_start=True`；`meta_up_at_end=True`；`tun_state_changed=False`；**只观察** |
| 10100 LISTEN | start/end 仅记录，未主动请求 `/v1/responses` |

---

## 4. `HARNESS_CODEX_PATH` 与环境继承

`child-environment-contract.txt`：

```text
HARNESS_CODEX_PATH_set_before_server=True
HARNESS_CODEX_PATH_set_before_host=True
HARNESS_CODEX_PATH_set_before_C=True
HARNESS_CODEX_PATH_value_path=<fixed native 0.146.0>
HARNESS_CODEX_PATH_sha256=bc343ba420dc2e2e9f59e6fc5e5bf0aae1cd8c771fc319665241fc9c0271fddb
```

共同子环境：`OMNIGENT_DATA_DIR`（本 RUN data）、`NO_PROXY=127.0.0.1,localhost`、`PYTHONUTF8`、`PYTHONIOENCODING`、`HARNESS_CODEX_PATH`。  
**实际 native child：** 本 RUN **未观察到** codex child（`actual_child_path=NOT_SPAWNED`）。

---

## 5. Observer

| 项 | 结果 |
|---|---|
| 业务前 `node --check` | **exit=0 / syntax_ok=True** |
| path/size/SHA | 已记录；业务中 SHA 与 frozen 一致 |
| 采样覆盖 | **失败**：`sample_count=0`，无连续 ordinal 覆盖 C 窗 |
| 事件 JSONL | 实质为空占位 |

Observer 在 server 启动前完成 syntax 预检；业务中途未改 observer 文件。

---

## 6. Server / Host

| 阶段 | 结果 |
|---|---|
| Server | READY + 连续 10s health=200（`server-ready.txt` / lifecycle live） |
| Host | `host_process_alive=True`，`process=online`，`host_status=online`（`daemons[]` schema）后才进入 C |
| 业务终态时 | server/host 仍 alive；server health 仍 True（业务结果文件） |

---

## 7. 单次 Controller C

| 项 | 值 |
|---|---|
| 命令形态 | `omnigent-zh.exe run <agent_dir> -p "Reply with CONTROLLER_OK and stop." --server http://127.0.0.1:55518` |
| agent | 目录镜像 `agents\controller\config.yaml`；`name=controller-d2-cli0146`；**harness=codex**；**model=gpt-5.6-sol** |
| attempt | **1_of_1**（本 RUN 无重试、无换端口续跑、无换模型） |
| 产品 idle watchdog | **240s 未改** |
| 外层预算记录 | 声明 300s；**实际 ~4s 被标为 outer_budget_timeout（编排缺陷，见上）** |
| 脱敏错误 | `turn setup failed: config.yaml missing required field: spec_version` |
| CONTROLLER_OK / assistant sentinel | **False** |
| 0202 workspace 400 | **False** |
| 10100/426 | **False** |
| runner_spawned | **False** |
| codex_child_spawned | **False** |

`d2-spawn-window.txt` 互斥布尔（由本 RUN 记录）：

```text
runner_spawned=False
codex_child_spawned=False
codex_child_early_exit=False
codex_child_alive_without_events=False
codex_events_seen_by_runner=NOT_OBSERVABLE
events_seen_by_omnigent_relay=NOT_OBSERVABLE
events_seen_by_cli=False
business_success=False
```

**business exit 与 cleanup exit：** cleanup 文件声明 `cleanup_does_not_replace_business_exit=True`；业务结果在 cleanup 前写入。但业务 `c_exit` 为空、timeout 标记不可信，故 **exit 分离在审计上仅部分成立**。

---

## 8. Evidence 顺序与自检

| 步骤 | 结果 |
|---|---|
| d2 live evidence + `d2-required-files-check` | 在 `d2-outcome` **之前**；文件存在性 pass（**未**严格要求 sample 条数>0） |
| cleanup | 本 RUN PID dead；port free；runtime 删除；`.codex-tmp` start=end；leftover=0 |
| `DIAGNOSIS` / `d2-outcome` / `run-summary` | cleanup 结果已知后**首次**写入并冻结 |
| `required-evidence-final-check` | finalPass=True（记录于 summary） |
| `evidence-manifest` | 已生成 |
| `leak-scan` | **最后文件**；`files_present_before_scan=47` / `files_scanned=47`；hits=0；`pass=True` |
| evidence 持久 | **未删除** evidence 根 |

未事后重建 live sample；未执行 D0/D1/后五轮 Gate 2。

---

## 9. 禁止项与 Gate 边界

- 未修改 `omnigent/`、`tests/`、政策、`STATUS.md`、用户 Codex/代理/认证/TUN 配置  
- 未 commit / push / merge / tag  
- 仓库仅新增本报告（及 handoffs 目录内既有交付）  
- Gate 1：相对 main **PASS**，非全仓 GREEN  
- Gate 2 r4：仍 **FAIL**  
- 本诊断 **≠ Gate 2 verdict**；**不可 merge**  
- TUN 开启仅为环境事实，**不是**根因证明  

---

## 10. 根因边界与给 Codex 的请求

### 已能说清

- 固定 CLI **0.146.0** native 身份在本 RUN start=end 可审计。  
- `HARNESS_CODEX_PATH` 在 server/host/C **前**注入。  
- server READY+10s、host 双 online 后才跑 C。  
- **本 RUN 未观察到 runner / native codex child**；C 在 turn setup 阶段以 agent 规格错误失败（stderr 脱敏）。  

### 不能说清 / 需 RO 注意

- 1s observer **未**覆盖 C 窗 → 不能用本 RUN 强证 “native 存活无事件” 或 “relay 丢失”。  
- 外层 4s timeout 标记 **不代表** 产品 240s idle watchdog。  
- 本地 agent 含 `spec_version: 1` 与 runner 报 “missing spec_version” 的矛盾，指向 **agent 上传/打包路径** 或 **目录镜像 vs 单文件 launcher** 的产品行为，需 Codex/Hermes 另卡查（**禁止本诊断改源码**）。  

### 建议（仅交回，不在本卡执行）

1. Codex RO 验收本 evidence；若因 sample/exit 不可审计，改判 **`DIAG_INCONCLUSIVE`** 并另发重跑卡。  
2. 若接受 `DIAG_RUNNER_SPAWN`：另发 Hermes 卡排查 **remote agent image 打包是否丢 `spec_version` / 是否必须单文件 launcher 形态**，以及 C 在 host 拓扑下的 runner 启动路径。  
3. 重跑卡必须：新 RUN_ID；修复编排 wait/observer 后 **仍然只允许一次 C**；保持 0.146.0 SHA + `HARNESS_CODEX_PATH` + 240s idle 不变。  

---

## 11. 完成标准对照（摘要）

| 要求 | 状态 |
|---|---|
| 全新 RUN_ID/evidence/runtime/端口 | 满足（本报告 RUN） |
| 固定 0.146.0 native | 满足 |
| HARNESS 在 server/host/C 前 | 满足 |
| TUN 只观察 | 满足 |
| observer 业务前 node --check | 满足；**采样失败** |
| server READY+10s / host online 后 C | 满足 |
| 只一次 C；无 D0/D1/后五轮 | 满足（本 RUN） |
| 240s idle 未改 | 满足 |
| 1s sample 覆盖 C | **未满足（0 samples）** |
| diagnosis 冻结后不改 | 满足 |
| leak-scan 最后 hits=0 | 满足 |
| evidence 持久 | 满足 |
| 唯一仓库交付本文件 | 满足 |
| 未改源码/tests/政策/STATUS/配置 | 满足 |
| 未 commit/push/merge/tag | 满足 |

---

## 12. 停止

**任务 18 诊断执行结束。**  
Evidence 根仍在：`C:\Users\Administrator\omnigent-diagnostics\20260730-190615-dc83140-grok-d2-c-cli0146-r1`。  
交回 **Codex 只读验收**。
