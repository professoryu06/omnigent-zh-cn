# HERMES_DIAGNOSIS_20 — HTTP / Session Bundle 只读回环诊断

**执行者：** Hermes（只读诊断执行者，非开发者，非 Gate 2 签字人）
**日期：** 2026-07-30
**工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
**HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`
**分支：** `docs/fix-plans-core-secondary`

---

## Primary

```
DIAG_HTTP_SESSION_READY_FOR_D2
```

所有 HTTP/session/artifact/hash/config 断言均通过。阶段 18 的 `config.yaml missing required field: spec_version` 错误**未在真实 HTTP/session 路径复现**。

---

## RUN 信息

| 项目 | 值 |
|---|---|
| RUN_ID | `20260730-144404-dc83140-hermes-http-session-roundtrip-r1` |
| Evidence 路径 | `C:\Users\Administrator\omnigent-diagnostics\20260730-144404-dc83140-hermes-http-session-roundtrip-r1\` |
| Evidence 仍存在 | True |
| Runtime | 已删除（cleanup） |
| Server 端口 | 57619（已释放） |

## 次数限制

| 动作 | 限制 | 实际 |
|---|---|---|
| Server 启动 | 1_of_1 | 1 |
| HTTP Driver | 1_of_1 | 1 |
| POST /v1/sessions | 1_of_1 | 1 |
| GET /agent | 1_of_1 | 1 |
| GET /agent/contents | 1_of_1 | 1 |

## Identity 与九 Blob

HEAD start = end = `dc83140c73ceb12fa165753c1880c19f68da86f4`
Branch start = end = `docs/fix-plans-core-secondary`

| 文件 | 期望 Blob | Worktree Start | Worktree End | Match |
|---|---|---|---|---|
| `omnigent/chat.py` | `6c65a6b9...` | `6c65a6b9...` | `6c65a6b9...` | ✅ |
| `omnigent/cli.py` | `1a0e4ea9...` | `1a0e4ea9...` | `1a0e4ea9...` | ✅ |
| `omnigent/server/schemas.py` | `ea6ebbfb...` | `ea6ebbfb...` | `ea6ebbfb...` | ✅ |
| `omnigent/server/routes/sessions.py` | `0375e5f9...` | `0375e5f9...` | `0375e5f9...` | ✅ |
| `omnigent/server/bundles.py` | `40451999...` | `40451999...` | `40451999...` | ✅ |
| `omnigent/stores/artifact_store/local.py` | `fc52f20a...` | `fc52f20a...` | `fc52f20a...` | ✅ |
| `omnigent/runtime/agent_cache.py` | `774989fc...` | `774989fc...` | `774989fc...` | ✅ |
| `omnigent/server/app.py` | `f31cb466...` | `f31cb466...` | `f31cb466...` | ✅ |
| `tests/server/helpers.py` | `955636ad...` | `955636ad...` | `955636ad...` | ✅ |

九 blob start = end，全部匹配。

## TUN 与环境

```
meta_up_at_start=False
meta_up_at_end=False
tun_state_changed_by_hermes=False
```

TUN 仅观察，未开关/重启/重配。环境仅记录代理变量存在性，未记录任何值。

## 禁止进程确认

```
host_started=False
runner_started=False
controller_c_executed=False
native_codex_started=False
d0_d1_d2_gate2_executed=False
```

预检注记：首次检查发现 `codex.exe` PID 1156（用户自有 Codex CLI），用户确认后关闭，重检 count=0。

## 五层对照表

| 层 | Size | SHA-256 | spec_version | name | harness | model |
|---|---|---|---|---|---|---|
| source config | 228 | `e8c0754348f2f626...` | 1 | controller-http-session-cli0146 | codex | gpt-5.6-sol |
| materialized config | 228 | `e8c0754348f2f626...` | 1 | controller-http-session-cli0146 | codex | gpt-5.6-sol |
| request bundle | 340 | `91b2f24a5bb164fb...` | 1 | controller-http-session-cli0146 | codex | gpt-5.6-sol |
| stored artifact | 340 | `91b2f24a5bb164fb...` | — | — | — | — |
| retrieved bundle | 340 | `91b2f24a5bb164fb...` | 1 | controller-http-session-cli0146 | codex | gpt-5.6-sol |

- source SHA = materialized SHA = request root config SHA = retrieved root config SHA = `e8c0754348f2f626137f446de9352d3d5c701a4a2cda42ea45e500dd2eb6cec6`
- request bundle SHA = stored artifact SHA = retrieved bundle SHA = `91b2f24a5bb164fb5f10bf77ccc3d2e48fb4645dc90bd70dbb13252b794e245a`
- 所有层 size 一致（config=228, bundle=340）
- root_config_yaml_count = 1（request 和 retrieved 均为 1）

## HTTP 状态

| 请求 | Status | 关键响应 |
|---|---|---|
| POST /v1/sessions (multipart) | **201** | session_id 非空, agent_id 非空, agent_name=controller-http-session-cli0146 |
| GET /v1/sessions/{id}/agent | **200** | name=controller-http-session-cli0146 |
| GET /v1/sessions/{id}/agent/contents | **200** | Content-Type=application/gzip, X-Agent-Name=controller-http-session-cli0146, X-Agent-Session-Scoped=true |

## Live JSONL

```
data_lines=11
ordinal_continuous=True (1..11)
utc_monotonic=True
post_count=1
get_count=2
```

11 个 stage 按序：source_config → materialized_config → request_bundle → request_bundle_validation → session_create_response → stored_artifact_match → session_agent_response → session_contents_response → retrieved_bundle → retrieved_config → end_to_end_hash_compare

## Driver

```
driver_attempt=1_of_1
driver_exit=0
driver_timed_out=False
driver_elapsed=1.4s
```

## Artifact 快照

- READY 时：13 个文件（server 初始化产物）
- POST 后：新增 1 个 artifact，SHA/size 与 request bundle 完全匹配，匹配数恰好为 1

## Required-check

```
required_check_pass=True
所有必需 evidence 非空
driver SHA 与 marker/final 一致
live JSONL 11 行、ordinal 连续、UTC 单调
POST=1, GET=2
request/stored/retrieved SHA 三方一致
三份 root config 固定字段正确
artifact READY/POST 快照可审计
server READY+10s (10/10)
无 host/runner/C/native/D0/D1/D2/Gate
无事后重建 live evidence
```

## Cleanup

```
all_run_pids_dead=True
server_port_free=True
runtime_exists=False
evidence_exists=True
leftover_count=0
```

## 阶段 18 错误复现判定

阶段 18 报告的 `config.yaml missing required field: spec_version` 错误**未在本 RUN 的真实 HTTP/session 路径复现**。

- 上传前 bundle 已含 `spec_version: 1`
- `validate_agent_bundle(enforce_handler_allowlist=False)` 通过
- POST 201 成功创建 session-scoped agent
- GET contents 回取 bundle 字节与上传完全一致
- 回取 config.yaml 含 `spec_version: 1`

结论：HTTP/session 预检路径已就绪，阶段 18 错误可能源于非 HTTP 路径（如 CLI 直接加载、runner 缓存、或旧 evidence 拼接）。

## 下一步

**建议 Codex 另发单次 D2 卡。**

本 RUN 证明 HTTP/session bundle 回环完整无误，可进入 D2 阶段验证。

## Gate 边界

- **本卡不是 D2 PASS。**
- **本卡不是 Gate 2 PASS。**
- **Gate 1 = PASS（相对 main），非全仓 GREEN。**
- **Gate 2 = FAIL（未在本 RUN 执行）。**
- **不可 merge。**

## 禁止项遵守声明

- 未修改源码、tests、政策、STATUS 或配置。
- 未启动 host、runner、Controller C、native Codex。
- 未执行 D0/D1/D2/Gate 2/Gate 1/pytest/ruff。
- 未重试、拼接旧 evidence。
- 未 commit/push/merge/tag。
- 未删除持久 evidence。
- 未记录任何 token、API key、Authorization、Bearer、Cookie、代理值或用户认证内容。
- 仓库仅新增 `HERMES_DIAGNOSIS_20.md`。
