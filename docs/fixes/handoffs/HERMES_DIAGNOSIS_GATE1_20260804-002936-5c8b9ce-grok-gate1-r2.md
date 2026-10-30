# HERMES_DIAGNOSIS_GATE1_20260804-002936-5c8b9ce-grok-gate1-r2

- **RUN_ID**: `20260804-002936-5c8b9ce-grok-gate1-r2`（全新 RUN_ID，未复用 r1）
- **执行者**: Hermes（用户明确授权 Gate 1 环境恢复与只读验收）
- **目标候选**: `5c8b9ce96f7552d380276fe6de04651f2b19531a`（worktree `F:\codex-ai\git项目部署\tmp\omnigent-gate1-cand`）
- **clean main 对照**: `81594243f7a17303b9ba477b938ac323f938c2e4`（origin/main，本地==远端，worktree `F:\codex-ai\git项目部署\tmp\omnigent-gate1-main`）
- **执行环境**: WSL2 Ubuntu-24.04（`C:\Program Files\WSL\wsl.exe` Store launcher），Python 3.12.3，uv 0.11.33
- **执行时间**: 2026-08-04 00:30~07:20 UTC+8（含 WSL 恢复诊断 + 双树全流程）
- **最终分类**: **GATE1_FAIL**

## 一、WSL 环境恢复（Phase 1）结论

- **阻塞根因（r1）**：Gate 1 r1 调用裸 `wsl.exe`（PATH 解析到 System32 inbox 版）报"系统找不到指定的路径"。
- **恢复结果**：**WSL 服务从未故障**——Store launcher `"/c/Program Files/WSL/wsl.exe" -d Ubuntu-24.04 -- uname -a` 正常返回
  `Linux DESKTOP-OLIHSDP 6.18.33.2-microsoft-standard-WSL2 ... x86_64 GNU/Linux`；`wsl -l -v` 显示 `Ubuntu-24.04 Running`。
- **最小恢复操作**：仅使用 Store launcher（本机固定模板），无需管理员权限/重启/重装/重新注册。
- 未执行：`wsl --unregister`、vhdx 删除/重建、evidence 删除、TUN/Clash/OpenCodex/10100 修改。
- 详见 `DIAGNOSIS_WSL_RECOVERY.md`（本 RUN evidence 根）。

## 二、执行记录（Phase 2）

| 步骤 | main（8159424） | cand（5c8b9ce） |
|------|-----------------|-----------------|
| uv sync --locked --extra dev | SYNC_EXIT=0 | SYNC_EXIT=0 |
| uv sync --locked --extra dev --extra all（补 databricks-sdk） | SYNC_ALL_EXIT=0 | SYNC_ALL_EXIT=0 |
| 完整 pytest（--timeout=300 --timeout-method=signal） | **138 failed**（EXIT=1） | **139 failed**（EXIT=1） |
| Ruff（规格 1.1 C 定向文件集） | 5 errors（全 E902 缺失文件） | 2 errors（全 E902 缺失文件） |
| compileall omnigent tests | EXIT=0 | EXIT=0 |

**执行方式修正记录**：
1. 初跑 `--extra dev` 时 `tests/inner/test_databricks_executor.py` 与 `test_openai_agents_sdk_executor.py` collection 失败（`ModuleNotFoundError: databricks`）——databricks-sdk 在 `all` extra（pyproject.toml:118，内部 CI 用 `--extra all`），补装后两侧正常 collection。
2. pyproject 默认 `timeout_method="thread"` 对 pytest_asyncio 测试失效（asyncio select 挂死不超时，无 JUnit）——改用 CLI `--timeout-method=signal`（CI 同款）后 pytest 完整跑完并产出 JUnit。

## 三、失败统计与差集

| 项 | 值 |
|----|-----|
| main 失败/错误 | 138 |
| cand 失败/错误 | 139 |
| 共享失败（nodeid 相同） | 138 |
| **candidate-only（新增）** | **1** |
| main-only | 0 |
| 共享失败语义指纹（归一化后） | **138/138 一致（mismatch=0）** |

## 四、新增失败详情（Gate 1 FAIL 依据）

```
nodeid: tests.inner.test_codex_executor::test_model_provider_override_appends_pin
main  : PASSED（time=0.012s，纯逻辑测试）
cand  : FAILED ×3（确定性，3 次独立重跑均失败）
断言  : executor._codex_config_overrides == ['model_provider="Databricks"']
实际  : ['features.network_proxy=true',
         'network_proxy.proxy_url="http://127.0.0.1:7897"',
         'model_provider="Databricks"']
位置  : tests/inner/test_codex_executor.py:2718
```

**根因**：候选 Commit 1（`e691d08c`，codex isolation 修复）在 `omnigent/inner/codex_executor.py` 新增 network_proxy 配置覆盖（+177/−6，含 `_CODEX_DEFAULT_PROXY = "http://127.0.0.1:7897"` 于 :153、`features.network_proxy=true` 与 `network_proxy.proxy_url` 于 :2311），**但未同步更新** `test_model_provider_override_appends_pin` 的断言（该测试期望 overrides 仅含 model_provider 一项）。测试文件在 main→cand 间**零改动**（`git diff main..cand -- tests/inner/test_codex_executor.py` 为空），实现变更破坏既有断言 = **候选引入的确定性代码失败**。

**排除**：非环境（0.012s 纯逻辑、无网络/资源依赖）、非 flaky（3 次重跑稳定失败）、非 main 既有失败（main PASSED）。

## 五、判定

**GATE1_FAIL** —— 按 PRE_MERGE_GATES.md Gate 1.2：*"集成树出现 main 没有的失败或 error → Gate 1 FAIL — 阻塞 merge"*。候选 `5c8b9ce` 相对 clean main（`8159424`）存在 **1 个确定性新增代码失败**，且不满足相对 PASS 安全条件（candidate-only failure、语义不同、无法归为 known_environment/known_flaky，`documented_main_code_failure` 需 Codex 显式批准且本失败为候选引入而非 main 代码失败）。

**补充记录**（不改变 FAIL 判定）：
- Ruff E902 ×(main 5 / cand 2) 均为规格 1.1 C 引用的文件在对应树中不存在（main 缺 4 个候选新增文件；cand 缺 `tests/inner/test_loader_executor_nested.py`、`tests/runner/test_codex_native_model_from_spec.py` 两个规格引用文件），**非真实 lint 违规**；两侧现存定向文件 ruff clean。
- compileall 两侧通过。
- 共享失败 138 个 nodeid 相同且归一化语义指纹一致（与 r6 2026-07-29 的 126 共享失败同模式，本 RUN 为 138）。

## 六、边界声明

- GATE1_FAIL **不等于**候选代码全坏：138/139 失败与 main 完全同源，唯一新增失败有明确 file:line 根因。
- 未修改源码/测试/STATUS/政策/配置；未执行 Gate 2、full-run、commit、push、merge、tag；凭据一律 `[REDACTED]`。
- 交付物为只读诊断文档（untracked），未入库。

## 七、证据文件

| 证据 | 路径 |
|------|------|
| 本报告 | `F:\codex-ai\git项目部署\tmp\omnigent-gate1-cand\docs\fixes\handoffs\HERMES_DIAGNOSIS_GATE1_20260804-002936-5c8b9ce-grok-gate1-r2.md` |
| RUN_ID / env / identity | `C:\Users\Administrator\omnigent-diagnostics\20260804-002936-5c8b9ce-grok-gate1-r2\RUN_ID.txt` / `env.txt` |
| WSL 恢复诊断 | `...\DIAGNOSIS_WSL_RECOVERY.md` |
| pytest JUnit ×2 | `...\main-sig-pytest.xml` / `cand-sig-pytest.xml` |
| pytest 输出 ×2 | `...\main-sig-pytest.txt` / `cand-sig-pytest.txt` |
| fail-ids ×2 + 差集 | `...\main-sig-fail-ids.txt` / `cand-sig-fail-ids.txt` / `new-failures-sig.txt` / `shared-fail-ids.txt` |
| 语义指纹比较 | `...\semantic_check.py` + `shared-semantic-summary.txt`（mismatch=0） |
| ruff / compileall / sync | `...\*-ruff.txt` / `*-compileall.txt` / `*-sync*.txt` / `run.log` |
