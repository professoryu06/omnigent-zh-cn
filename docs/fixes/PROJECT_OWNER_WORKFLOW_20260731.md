# Omnigent 主理人工作流（2026-07-31）

## 角色分工

- Codex：项目主理人。负责第一性原理拆解、任务卡、范围控制、版本管理、只读审查和最终裁决。
- Hermes：只读诊断员。负责日志、环境、网络、代码路径分析和修复方案；不直接改源码。
- Grok：实施员。只按已批准任务卡改源码/测试，运行指定测试，建立 Git checkpoint 和 evidence。

## 固定顺序

1. Codex 明确问题边界、影响面、禁止事项和验收判据。
2. Hermes 只读确认根因并写诊断/方案。
3. Codex 审查 Hermes 方案，决定是否发实施卡。
4. Grok 按实施卡修改并测试，不得扩大范围。
5. Codex 只读审查 diff、测试、evidence、回滚点。
6. 只有 Codex 验收通过后，才允许进入下一张卡；Gate 1/2 另行签字。

## 当前任务拆解

### 卡 25A：Windows 路径测试债务

Hermes 先确认 `tests/test_codex_native_state.py` 的 `/repo` 等路径是否纯属测试可移植性问题，
并给出 `Path`/`PurePosixPath` 的最小修复方案。Grok 只能修改测试夹具或平台条件，不能放宽产品绝对路径校验。

### 卡 25B：Codex 隔离审查

Hermes 审查候选版是否保持私有 `CODEX_HOME`、订阅 auth、OpenCodex 10100 隔离、模型固定和
配置清洗；不得直接带入 review 分支尚未成功的 Route-A 代理实现。

### 卡 25C：单次 full-run

仅在 25A/25B 审查通过后，由 Grok 用新 RUN_ID 执行一次 Windows Codex 0.146.0 full-run。
判据必须包含真实 assistant、`turn/completed`、C exit=0、无 10100 连接、OpenCodex 存活、
evidence 最后 leak-scan=0。单次 full-run 不等于 Gate 2 PASS。

### 卡 26：Gate 1 / Gate 2

full-run 通过后才开 Gate 1；Gate 2 六轮必须独立执行和验收，未完成前不可 merge。

## 交付和版本规则

- 每张卡使用新 RUN_ID、新 evidence、新 handoff，不覆盖旧报告。
- Grok 修改前必须创建 Git checkpoint；完成后提交并写明回滚 commit/tag。
- 凭据一律 `[REDACTED]`；evidence、VHDX、旧文档不得删除。
- 新资料必须写入仓库 `docs/fixes/` 或 `docs/fixes/handoffs/`，并同步到 Obsidian `Omnigent/`。
- Codex 不在主理审查阶段自行重跑业务 full-run，除非用户另行授权。
