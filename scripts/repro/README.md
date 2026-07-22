# 复现与验收

## 重要

`matrix-*.md` 中的表格若无「命令 + 产物路径」则只是 **checklist**，**不是**可运行矩阵。

可运行复现优先放在 **pytest**（`tests/`），与仓库既有框架一致。  
仅跨进程/平台行为才用本目录脚本。

## 每个用例必须记录

| 字段 | 说明 |
|------|------|
| upstream / zh-cn commit | `git rev-parse HEAD` |
| OS / Python / Omnigent | 版本字符串 |
| setup / teardown | 环境与清理 |
| 命令 | 完整 pytest/脚本行 |
| 故障注入 | 如何制造失败条件 |
| 断言 | 确定性条件 |
| 超时 | pytest-timeout 或脚本 |
| 预修复结果 | FAIL + 日志路径 |
| 修复后结果 | PASS + 日志路径 |
| 产物目录 | 默认 `artifacts/repro/<case-id>/`（gitignore） |

## 用例 ID

| ID | Issue | 实现位置（目标） |
|----|-------|------------------|
| C-3016 | #3016 | `tests/runner/test_session_workspace_cache.py` |
| C-2853 | #2853 | `tests/inner/test_native_system_prompt_delivery.py` |
| C-2747 | #2747 | `tests/inner/test_loader_executor_nested.py` |
| C-2746 | #2746 | `tests/runner/test_codex_native_model_from_spec.py` |
| C-2854 | #2854 | TBD |
| C-2539 | #2539 | TBD |
| C-2967 | #2967 | TBD |

## 结果产物

```text
artifacts/repro/   # gitignored；本地/CI 可选上传
```

禁止提交凭证、token、用户主目录路径、真实敏感 prompt。
