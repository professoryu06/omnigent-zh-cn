# GROK DIAGNOSIS 19 — Agent Bundle / Observer 只读预检

> **角色：** Grok（只读诊断执行者）  
> **任务卡：** `docs/fixes/handoffs/CODEX_TASK_19.md`  
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
> **唯一仓库交付：** 本文件  

---

## 1. 唯一分类

```text
DIAG_INCONCLUSIVE
```

| 字段 | 值 |
|---|---|
| **原因** | `preflight_required_files_pass=False`（observer 正向 required-check 形式失败：`observer_exit` 未写入 / `observer_positive_pass=False`），按任务矩阵 required-check 不可审计 → **INCONCLUSIVE** |
| pipeline_attempt | **1_of_1** |
| observer_attempt | **1_of_1** |
| controller_c_executed | **False** |
| server/host/runner/native_codex_started | **False / False / False / False** |
| full_gate2_executed | **False** |

**实质业务结果（供 RO 复核，不改冻结 outcome）：**

- Offline agent pipeline：**六层全 PASS**，`spec_version=1` 未丢失，`bundle_sha256 == artifact_roundtrip_sha256`。  
- Observer live：**5** 条连续 sample（ordinal 1..5，utc 单调，sentinel_seen=5，query_exit 全 0）。  
- 零样本负向：`zero_sample_data_line_count=0`，`zero_sample_required_check_pass=False`（**正确 FAIL**）。  
- 形式失败点：`Start-Process` 未记录 `ExitCode`（`observer_exit=` 空），导致 `observer-required-check.pass=False`，进而 overall required-check FAIL。

**不是** Gate 2 PASS；**不是** D2 授权；**不可 merge**。

---

## 2. RUN / Evidence

| 项 | 值 |
|---|---|
| **RUN_ID** | `20260730-192929-dc83140-grok-agent-observer-preflight-r1` |
| **Evidence（持久）** | `C:\Users\Administrator\omnigent-diagnostics\20260730-192929-dc83140-grok-agent-observer-preflight-r1` |
| **Runtime** | `%TEMP%\omnigent-agent-observer-preflight-...`（**已删除**） |
| **报告时 evidence 存在** | **True** |

未拼接阶段 14–18 / r4 的 PID/sample/exit。未启动 Omnigent server/host/runner/C/native Codex。

---

## 3. Identity / 七 blob / TUN / native 观察

| 检查 | 结果 |
|---|---|
| HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` start=end |
| branch | `docs/fix-plans-core-secondary` |
| 七相关 blob | start/end `all_match=True`（chat/cli/spec/parser/bundles/local artifact/agent_cache） |
| precheck residual | count=0 / pass=True |
| TUN Meta | start Up / end Up；`tun_state_changed_by_grok=False`；只观察 |
| native | size=358650672 SHA=`bc343ba4…` 与任务卡一致；**native_executed=False**（未跑 --version/prompt） |

---

## 4. 脚本冻结

| 项 | 结果 |
|---|---|
| `python -m py_compile` | exit=0 |
| `node --check` | exit=0 |
| `preflight-start-marker` | scripts_frozen=True 后未改脚本 |
| pipeline SHA | start=end |
| observer SHA | start=end |

---

## 5. Offline agent bundle pipeline（1_of_1）

固定 source（evidence 原样保存）：

```yaml
spec_version: 1
name: controller-preflight-cli0146
executor.type: omnigent
executor.config.harness: codex
executor.config.model: gpt-5.6-sol
```

### 六层对照

| 层 | spec_version | name | harness | model | 结论 |
|---|---|---|---|---|---|
| source | 1 | controller-preflight-cli0146 | codex | gpt-5.6-sol | PASS |
| materialized | 1 | controller-preflight-cli0146 | codex | gpt-5.6-sol | PASS |
| bundle root config.yaml | 1 | controller-preflight-cli0146 | codex | gpt-5.6-sol | PASS |
| server `validate_agent_bundle` | 1 | controller-preflight-cli0146 | codex | gpt-5.6-sol | PASS |
| artifact store put/get roundtrip | 1 | controller-preflight-cli0146 | codex | gpt-5.6-sol | PASS |
| AgentCache.load + workdir config | 1 | controller-preflight-cli0146 | codex | gpt-5.6-sol | PASS |

### Bundle / artifact

| 项 | 值 |
|---|---|
| bundle_member_config_yaml_count | **1** |
| bundle_config_at_root | **True** |
| bundle_sha256 | `8d3f03a881a175f5f3bb31145635491b6a9a36cac829b0f40b72e935b3d04d57` |
| artifact_roundtrip_sha256 | **相同** |
| bundle_size / roundtrip_size | **334 / 334** |
| pipeline_stage_count | **11** |
| pipeline_ordinals_continuous | **True** |
| first_failing_boundary | **None** |
| pipeline exit | **0** |
| all_layers_pass | **True** |

调用顺序（live `pipeline-boundaries-live.jsonl`）：  
canonicalize → materialize → validate_agent_spec → bundle_agent → bundle_read_config → server_validate_agent_bundle → bundle_location → artifact_put → artifact_get_roundtrip → agent_cache_load → agent_cache_config_read。

**边界解释：** 离线 CLI materialize → bundle → server validate → LocalArtifactStore → AgentCache 路径**未丢失** `spec_version`。  
**不得**据此宣称阶段 18 HTTP/session/host/runner 远端路径已通过；阶段 18 报错仍可能出在上传/session 包装层。

---

## 6. Observer sentinel 预检（1_of_1）

| 项 | 值 |
|---|---|
| sentinel | 诊断自有 `node sentinel.js` ~8s；非 Omnigent/Codex |
| live samples | **5**（`observer-live.jsonl`） |
| ordinals | **1..5 精确连续** |
| utc_monotonic | **True** |
| sentinel_seen_count | **5**（≥3） |
| query_exit_nonzero_count | **0** |
| observer_stderr_empty（过程记录） | **True** |
| observer_sha start=end | **True** |
| observer_exit 记录 | **空**（形式缺陷） |
| observer-required-check.pass | **False**（因 exit 空） |

### 零样本负向

| 项 | 值 |
|---|---|
| zero_sample_data_line_count | **0** |
| zero_sample_required_check_pass | **False** |
| 与正向同一函数 | `Test-ObserverLiveRequired` |
| 负向自检 pass（期望 FAIL 且得到 FAIL） | **True** |

**结论：** observer **能**实时连续采样；**零样本必使 required-check FAIL** 已证明。形式 required 因 exit 码未落盘未 PASS。

---

## 7. Evidence 顺序

```text
preflight-required-files-check (FAIL)
  → cleanup / end identity
  → preflight-outcome + run-summary + GROK_DIAGNOSIS_19
  → required-evidence-final-check
  → evidence-manifest
  → leak-scan（最后）
```

| 步骤 | 结果 |
|---|---|
| required-check | **FAIL**（observer_positive_pass=False） |
| cleanup | runtime 删除；PID dead；evidence 保留 |
| outcome 冻结 | `DIAG_INCONCLUSIVE` |
| leak-scan | 见 evidence 末文件 |

---

## 8. 建议（不自行执行）

1. **Codex RO 验收**本卡：离线 bundle 路径已证明 `spec_version` 可贯穿；observer 采样能力与零样本负向已证明。  
2. 若 RO 接受实质结果：可改判旁注「pipeline 就绪 / observer 实质就绪」，但正式 primary 以冻结 `DIAG_INCONCLUSIVE` 为准，或授权 **observer 退出码落盘修复后的重跑预检卡**（仍禁止本会话改 outcome）。  
3. **下一步 D2**：离线 pipeline PASS 不等于远端 session 路径 PASS。建议 Codex 决定：  
   - 先做 HTTP/session agent roundtrip 只读卡，或  
   - 直接发新单次 D2 卡（修复编排 exit 记录 + 保持 1s sample required 严格）。  
4. **Hermes：** 本卡 **不**建议仅因 offline pipeline 发 Hermes；阶段 18 `missing spec_version` 若仍复现，应在 **上传/HTTP/session** 边界另开只读卡定位，而非改 parser（offline 已通）。

---

## 9. Gate 边界

- Gate 1：相对 main **PASS**，非全仓 GREEN  
- Gate 2 r4：**FAIL**  
- 本卡 **不是** Gate 2 PASS；**不是** `DIAG_PREFLIGHT_READY_FOR_D2`（因 required-check 形式 FAIL）  
- **不可 merge**  
- 未改源码/tests/政策/STATUS/TUN/认证；未 commit/push/merge/tag  

---

## 10. 停止

Evidence 根仍存在。交回 **Codex 只读验收**。停止。