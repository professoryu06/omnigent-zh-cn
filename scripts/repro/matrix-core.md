# 核心验收矩阵（可运行规格）

> Markdown 表 = 规格说明。执行以 pytest 为准。
> 证据标签：已证实 / 未复现 / 仅上游报告 / 已被上游修复 / **mitigated(fail-loud)**。
> 可审计证据优先：test-first commit + 可复跑命令；本地 `artifacts/` 仅辅助，不可作为唯一证明。

## 固定记录头（每次 run 填写）

```yaml
zh_cn_commit: "<git rev-parse HEAD>"
upstream_ref: "optional"
os: "Windows / Linux / macOS + version"
python: "3.12.x"
omnigent_version: "from importlib.metadata or pyproject"
commands: |
  uv run pytest <paths> -q
artifacts_dir: "artifacts/repro/<date>/  # optional local only"
```

## C-3016 workspace 投影缓存

| 项 | 内容 |
|----|------|
| Issue | #3016 |
| Setup | `create_runner_app` + MockTransport；workspace worktree ≠ runner global |
| Fault | 第一次 `GET /v1/sessions/{id}` 非 200；第二次 200 + 有效 workspace |
| Assert | 失败不毒化缓存；重试后 cwd/changes 用 session worktree；reset 驱逐 projection |
| Command | `uv run pytest tests/runner/test_session_workspace_cache.py -q` |
| Timeout | 30s |
| Pre-fix | FAIL（毒化）— 见 test-first commit on PR #3 |
| Post-fix | PASS |
| 证据标签 | **已证实** + 修复 PR open |

## C-2853 native system_prompt（两阶段）

### Phase 1 — fail-loud / mitigation（当前）

| 项 | 内容 |
|----|------|
| 状态 | **mitigated / fail-loud**（**不是**完整 fixed） |
| 覆盖 | helper + 各 native executor `run_turn`：warn / strict error；日志不含 prompt 原文 |
| 命令 | `uv run pytest tests/inner/test_native_system_prompt_delivery.py -q` |
| 未声称 | **未**完成逐 CLI capture double 安全 apply；角色 prompt **仍可能未送达** |
| Strict | 仅环境变量 `OMNIGENT_STRICT_PROMPT`（无 per-agent YAML 字段） |

### Phase 2 — safe apply（开放）

| 项 | 内容 |
|----|------|
| 目标 | 逐 CLI capture double：argv / stdin / 配置 / session-init 安全通道 |
| 状态 | **未实现**；能力矩阵保持开放 |
| 非断言 | 不得仅依赖模型是否写 commit trailer |

## C-2747 nested executor config.harness

| 项 | 内容 |
|----|------|
| Command | `uv run pytest tests/inner/test_loader_executor_nested.py -q` |
| Assert | 最终 `harness_kind == "codex-native"`（无条件） |
| 证据标签 | **已证实** |

## C-2746 codex-native model 字段

| 项 | 内容 |
|----|------|
| Command | `uv run pytest tests/runner/test_codex_native_model_from_spec.py -q` |
| 证据标签 | **已证实** |

## C-2854 / C-2539 / C-2967

规格见 CORE_FIX_PLANS；**仅上游报告**（本轮未做可运行用例）。
