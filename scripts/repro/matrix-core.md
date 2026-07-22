# 核心验收矩阵（可运行规格）

> Markdown 表 = 规格说明。执行以 pytest 为准。  
> 证据标签：已证实 / 未复现 / 仅上游报告 / 已被上游修复。

## 固定记录头（每次 run 填写）

```yaml
zh_cn_commit: "<git rev-parse HEAD>"
upstream_ref: "optional"
os: "Windows / Linux / macOS + version"
python: "3.12.x"
omnigent_version: "from importlib.metadata or pyproject"
commands: |
  uv run pytest tests/runner/test_session_workspace_cache.py -q
artifacts_dir: "artifacts/repro/<date>/"
```

## C-3016 workspace 投影缓存

| 项 | 内容 |
|----|------|
| Issue | #3016 |
| Setup | `create_runner_app` + MockTransport；workspace worktree path ≠ runner global |
| Fault | 第一次 `GET /v1/sessions/{id}` → 非 200 且无 workspace；第二次 → 200 + 有效 workspace |
| Assert | 失败不写入可恢复毒化；重试后 runtime cwd = session workspace；reset-agent-cache 驱逐 workspace cache |
| Command | `uv run pytest tests/runner/test_session_workspace_cache.py -q` |
| Timeout | 30s |
| Pre-fix | 期望 FAIL（毒化） |
| Post-fix | 期望 PASS |

## C-2853 native system_prompt

| 项 | 内容 |
|----|------|
| Issue | #2853 |
| Setup | 唯一 sentinel；native executor/harness 用 capture double 替换真实 CLI |
| Assert | sentinel 到达承诺通道 **或** 明确 warn/strict error；禁止静默 |
| Command | `uv run pytest tests/inner/test_native_system_prompt_delivery.py -q` |
| 非断言 | 不得仅依赖模型是否写 commit trailer |

## C-2747 nested executor type/config

| 项 | 内容 |
|----|------|
| Issue | #2747 |
| Setup | 最小 YAML：`type: omnigent` + `config.harness: codex-native` + 会触发错误推断的 model 前缀 |
| Assert | harness 不被静默换成 model-prefix 结果；或响亮错误 |
| Command | `uv run pytest tests/inner/test_loader_executor_nested.py -q` |

## C-2746 codex-native model 字段

| 项 | 内容 |
|----|------|
| Issue | #2746 |
| Setup | AgentSpec `executor.model` 有值、`config` 无 `model` |
| Assert | `_codex_native_model_from_spec` 返回 `executor.model` |
| Command | `uv run pytest tests/runner/test_codex_native_model_from_spec.py -q` |

## C-2854 / C-2539 / C-2967

规格见 CORE_FIX_PLANS；实现待补。当前标签：**仅上游报告**（无本仓库可运行用例前）。
